from conans import ConanFile, CMake, tools
import os

class GrapheneConan(ConanFile):
    name = "graphene"
    version = "1.4.0"
    description = "A thin layer of graphic data types"
    url = "https://github.com/conanos/graphene"
    homepage = "https://github.com/conanos/graphene"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "glib/2.58.0@conanos/dev"

    source_subfolder = "source_subfolder"

    def source(self):
        url_ = 'https://github.com/ebassi/graphene/archive/{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        os.rename("%s-%s"%(self.name, self.version), self.source_subfolder)
        
    def build(self):
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

