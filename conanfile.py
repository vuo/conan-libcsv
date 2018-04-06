from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform

class LibcsvConan(ConanFile):
    name = 'libcsv'

    source_version = '3.0.3'
    package_version = '3'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-libcsv'
    license = 'https://sourceforge.net/projects/libcsv/'
    description = 'A library for reading and writing comma-separated data files'
    source_dir = 'libcsv-%s' % source_version
    build_dir = '_build'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://sourceforge.net/projects/libcsv/files/libcsv/libcsv-%s/libcsv-%s.tar.gz' % (self.source_version, self.source_version),
                  sha256='d9c0431cb803ceb9896ce74f683e6e5a0954e96ae1d9e4028d6e0f967bebd7e4')

        self.run('mv %s/COPYING.LESSER %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = ['c++abi']

            autotools.flags.append('-Oz')
            autotools.flags.append('-Wno-error')

            if platform.system() == 'Darwin':
                autotools.flags.append('-mmacosx-version-min=10.10')
                autotools.link_flags.append('-Wl,-headerpad_max_install_names')
                autotools.link_flags.append('-Wl,-install_name,@rpath/libcsv.dylib')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    args=['--quiet',
                                          '--enable-shared',
                                          '--disable-static',
                                          '--prefix=%s' % os.getcwd()])
                autotools.make(args=['install'])

            if platform.system() == 'Linux':
                patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                self.run('%s --set-soname libcsv.so lib/libcsv.so' % patchelf)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        self.copy('libcsv.%s' % libext, src='%s/lib' % self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['csv']
