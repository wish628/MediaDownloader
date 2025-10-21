from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import shprint, current_directory
from os.path import join, exists
import sh
import os

class FFMpegRecipe(Recipe):
    version = 'n6.0'
    url = 'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-android-arm64-gpl.zip'
    depends = ['python3']
    patches = []
    opt_depends = []
    
    def should_build(self, arch):
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libffmpeg.so'))
    
    def build_arch(self, arch):
        super(FFMpegRecipe, self).build_arch(arch)
        
        # Download FFmpeg binary for Android ARM64
        build_dir = self.get_build_dir(arch.arch)
        with current_directory(build_dir):
            if not exists('ffmpeg'):
                # Download the FFmpeg binary
                self.download_file(self.url, 'ffmpeg.zip')
                # Extract the zip file
                shprint(sh.unzip, 'ffmpeg.zip')
                
                # Copy the binary to the libs directory
                libs_dir = self.ctx.get_libs_dir(arch.arch)
                if not exists(libs_dir):
                    os.makedirs(libs_dir)
                    
                # Copy the FFmpeg binary
                shprint(sh.cp, '-f', 'ffmpeg', libs_dir)
                
                # Make it executable
                shprint(sh.chmod, '+x', join(libs_dir, 'ffmpeg'))

recipe = FFMpegRecipe()