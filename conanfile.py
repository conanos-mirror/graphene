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
    default_options = { 'shared': False, 'fPIC': True }
    requires = "glib/2.58.1@conanos/stable"

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        config_scheme(self)
    
    def configure(self):
        del self.settings.compiler.libcxx

    #def is_msvc(self):
    #    return  self.settings.compiler == 'Visual Studio'


    #def build_requirements(self):
    #    if self.is_msvc:
    #        #self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")
    #        self.build_requires("msys2_installer/20161025@bincrafters/stable")

    #def requirements(self):
    #    assert(0)
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
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        meson = Meson(self)
        meson.configure(defs=defs, source_dir = self._source_subfolder,
                        build_dir=self._build_subfolder,pkg_config_paths=pkg_config_paths)
        meson.build()
        self.run('ninja -C {0} install'.format(meson.build_dir))

    #def gcc_build(self):
    #    with tools.chdir(self._source_subfolder):
    #        _args = ['--prefix=%s/builddir'%(os.getcwd()), '--libdir=%s/builddir/lib'%(os.getcwd()), '--disable-maintainer-mode',
    #                 '--disable-silent-rules', '--disable-arm-neon']
    #        if self.options.shared:
    #            _args.extend(['--enable-shared=yes','--enable-static=no'])
    #        else:
    #            _args.extend(['--enable-shared=no','--enable-static=yes'])

    #        self.run('sh autogen.sh %s'%(' '.join(_args)))#space
    #        self.run('make -j2')
    #        self.run('make install')

    def package(self):
        #if tools.os_info.is_linux:
        #    with tools.chdir(self._source_subfolder):
        #        self.copy("*", src="%s/builddir"%(os.getcwd()))
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

