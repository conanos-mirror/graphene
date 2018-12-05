from conans import ConanFile, CMake, tools,Meson
from conanos.build import config_scheme
import os

def to_unicode(filename):
    f = open(filename, mode='r', encoding='UTF-8')
    content = f.read()
    f.close()
    f = open(filename,'w',encoding='UTF-16')
    f.write(content)
    f.close()

class GrapheneConan(ConanFile):
    name = "graphene"
    version = "1.8.2"
    description = "A thin layer of graphic data types"
    url = "https://github.com/conanos/graphene"
    homepage = "https://github.com/conanos/graphene"
    license = "MIT"
    generators = "gcc","visual_studio"
    patch = "windows-warning-c4244.patch"
    exports = [patch]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        'fPIC': [True, False]
    }
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)
    
    def requirements(self):
        self.requires.add("glib/2.58.1@conanos/stable")

    def build_requirements(self):
        self.build_requires("libffi/3.299999@conanos/stable")

    def source(self):
        url_ = 'https://github.com/ebassi/graphene/archive/{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        if self.settings.os == 'Windows':
            tools.patch(patch_file=self.patch)
        os.rename("%s-%s"%(self.name, self.version), self._source_subfolder)
        if self.settings.os == 'Windows':
            to_unicode(os.path.join(self._source_subfolder,'src/graphene-euler.c'))

    def build(self):
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in ["glib","libffi"] ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix':prefix, 'introspection':'false'}
        meson = Meson(self)
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
            libpath = [ os.path.join(self.deps_cpp_info[i].rootpath, "lib") for i in ["glib","libffi"] ]
            with tools.environment_append({
                'LD_LIBRARY_PATH' : os.pathsep.join(libpath)
                }):
                meson.configure(defs=defs, source_dir = self._source_subfolder,
                                build_dir=self._build_subfolder,pkg_config_paths=pkg_config_paths)
                meson.build()
                self.run('ninja -C {0} install'.format(meson.build_dir))
        
        if self.settings.os == 'Windows':
            meson.configure(defs=defs, source_dir = self._source_subfolder,
                                build_dir=self._build_subfolder,pkg_config_paths=pkg_config_paths)
            meson.build()
            self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

