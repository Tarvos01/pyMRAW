# www.ladisk.si
#
# pyMRAW is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# pyMRAW is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyMRAW.  If not, see <http://www.gnu.org/licenses/>.
"""
This module is reads Photron MRAW image sequences.

Author: Jaka Javh (jaka.javh@fs.uni-lj.si), Janko Slavič (janko.slavic@fs.uni-lj.si) www.ladisk.si

We developed this module while working on this publication:
J. Javh, J. Slavič and M. Boltežar: The Subpixel Resolution of Optical-Flow-Based Modal Analysis,
Mechanical Systems and Signal Processing, Vol. 88, p. 89–99, 2017
 
If you find it useful, consider to cite us.
"""
import numpy as np
import warnings

__version__ = '0.10'

SUPPORTED_FILE_FORMATS = ['mraw', 'tiff']
SUPPORTED_EFFECTIVE_BIT_SIDE = ['lower', 'higher']

def get_cih(filename):
    cih = dict()

    # read the cif header
    f = open(filename, 'r')
    for line in f:
        if line == '\n': #end of cif header
            break
        line_sp = line.replace('\n', '').split(' : ')
        if len(line_sp) == 2:
            key, value = line_sp
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
                cih[key] = value
            except:
                cih[key] = value

    # check exceptions
    ff = cih['File Format']
    if ff.lower() not in SUPPORTED_FILE_FORMATS:
        raise Exception('Unexpected File Format: {:g}.'.format(ff))
    bits = cih['Color Bit']
    if bits < 12:
        warnings.warn('Not 12bit ({:g} bits)! clipped values?'.format(bits))
    elif (bits > 12):
        warnings.warn('Not 12bit ({:g} bits)! Values may/will be divided by /16->12bit (during operation)'.format(bits))
                # - may cause overflow')
                # 12-bit values are spaced over the 16bit resolution - in case of photron filming at 12bit
                # this can be meanded by dividing images with //16
    if cih['EffectiveBit Depth'] != 12:
        warnings.warn('Not 12bit image!')
    ebs = cih['EffectiveBit Side']
    if ebs.lower() not in SUPPORTED_EFFECTIVE_BIT_SIDE:
        raise Exception('Unexpected EffectiveBit Side: {:g}'.format(ebs))
    if (cih['File Format'].lower() == 'mraw') & (cih['Color Bit'] != 16):
        raise Exception('Not a 16bit file! Mraw only works for 16bit files.')  # or very slow
    if cih['Original Total Frame'] > cih['Total Frame']:
        warnings.warn('Clipped footage!')

    return cih

def load_images(mraw, h, w, N):
    """
    loads the next N images from the binary mraw file into a numpy array.
    Inputs:
        mraw - an opened binary .mraw file
        h - image height
        w - image width
        N - number of sequential images to be loaded
    Outputs:
        images[h, w, N]
    """
    images = np.memmap(mraw, dtype=np.uint16, mode='r', shape=(N, h, w))
    #images=np.fromfile(mraw, dtype=np.uint16, count=h * w * N).reshape(N, h, w) # about a 1/3 slower than memmap when loading to RAM. Also memmap doesn't need to read to RAM but can read from disc when needed.
    return np.rollaxis(images, 0, 3)

def show_UI():
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename
    from matplotlib import pyplot as plt
    from matplotlib import animation


    window = Tk()  # open window
    filename = askopenfilename(parent=window, title='Select the .cih file', filetypes=[
        ("Photron cih file", "*.cih")])  # open window to load the camera and files info
    window.destroy()  # close the tk window

    cih = get_cih(filename)
    N = cih['Total Frame']
    h = cih['Image Height']
    w = cih['Image Width']

    #if N > 12:
    #    N = 12
    mraw = open(filename[:-4] + '.mraw', 'rb')
    mraw.seek(0, 0)  # find the beginning of the file
    image_data = load_images(mraw, h, w, N)  # load N images
    #np.memmap in load_images loads enables reading an array from disc as if from RAM. If you want all the images to load on RAM imediatly use load_images(mraw, h, w, N).copy()
    mraw.close()

    fig = plt.figure()
    ax = plt.subplot()
    ms = ax.matshow(image_data[:, :, 0], cmap=plt.get_cmap('gray'), vmin=0,
                    vmax=2 ** 12)  # display data for first image


    def animate(i):
        ms.set_data(image_data[:, :, i])
        return [ms]


    anim = animation.FuncAnimation(fig, animate, frames=N, interval=1, blit=True)
    plt.show()


if __name__ == '__main__':
    show_UI()
    #a = get_cih('data/sample_60k_16bit.cih')
    #print(a)