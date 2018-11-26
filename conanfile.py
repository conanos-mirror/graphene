from conans import ConanFile, CMake, tools,Meson
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
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "glib/2.58.1@conanos/stable"

    source_subfolder = "source_subfolder"

    def is_msvc(self):
        return  self.settings.compiler == 'Visual Studio'


    def build_requirements(self):
        if self.is_msvc:
            #self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")
            self.build_requires("msys2_installer/20161025@bincrafters/stable")

    def requirements(self):
        assert(0)

    def source(self):
        url_ = 'https://github.com/ebassi/graphene/archive/{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        os.rename("%s-%s"%(self.name, self.version), self.source_subfolder)
        if self.is_msvc:
            to_unicode(os.path.join(self.source_subfolder,'src/graphene-euler.c'))

    def build(self):
        defs = {'prefix':self.package_folder}


        meson = Meson(self)
        meson.configure( defs=defs,
            source_dir=self.source_subfolder,
            build_dir='_build')
        meson.build()

        self.run('ninja -C {0} install'.format(meson.build_dir))
        


    def gcc_build(self):
        with tools.chdir(self.source_subfolder):
            _args = ['--prefix=%s/builddir'%(os.getcwd()), '--libdir=%s/builddir/lib'%(os.getcwd()), '--disable-maintainer-mode',
                     '--disable-silent-rules', '--disable-arm-neon']
            if self.options.shared:
                _args.extend(['--enable-shared=yes','--enable-static=no'])
            else:
                _args.extend(['--enable-shared=no','--enable-static=yes'])

            self.run('sh autogen.sh %s'%(' '.join(_args)))#space
            self.run('make -j2')
            self.run('make install')

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

