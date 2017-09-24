from conans import ConanFile, tools, AutoToolsBuildEnvironment
# import shutil
import os

class LibcsvConan(ConanFile):
    name = 'libcsv'
    version = '3.0.3'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-libcsv'
    license = 'https://sourceforge.net/projects/libcsv/'
    description = 'A library for reading and writing comma-separated data files'
    source_dir = 'libcsv-%s' % version
    build_dir = '_build'

    def source(self):
        tools.get('https://sourceforge.net/projects/libcsv/files/libcsv/libcsv-%s/libcsv-%s.tar.gz' % (self.version, self.version),
                  # sha256='d9c0431cb803ceb9896ce74f683e6e5a0954e96ae1d9e4028d6e0f967bebd7e4'
                  )

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.cxx_flags.append('-Oz')
            autotools.cxx_flags.append('-mmacosx-version-min=10.8')
            autotools.link_flags.append('-Wl,-install_name,@rpath/libcsv.dylib')
            autotools.configure(configure_dir='../%s' % self.source_dir,
                                args=['--quiet',
                                      '--enable-shared',
                                      '--disable-static',
                                      '--prefix=%s' % os.getcwd()])
            autotools.make(args=['install'])
            # libusb calls itself 1.0.0 regardless of the actual release version.
            # shutil.move('lib/libusb-1.0.0.dylib', 'lib/libusb.dylib')

    def package(self):
        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        self.copy('libcsv.dylib', src='%s/lib' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['csv']
