import sys
import numpy as np

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s <in-vtk-file> <out-txt-file>' % sys.argv[0])

    in_file = sys.argv[1]
    out_file = sys.argv[2]
    with open(in_file, mode='r') as f:
        meta = {}
        for i in range(0, 10):
            t = str(f.readline()).strip().split(' ')
            meta[t[0]] = t[1:]

        dims = None
        spacing = None
        origin = None
        n = None
        dtype = None
        for k in meta.keys():
            if k == 'DIMENSIONS':
                dims = (int(meta[k][0]), int(meta[k][1]), int(meta[k][2]))
            elif k == 'SPACING':
                spacing = (float(meta[k][0]), float(meta[k][1]), float(meta[k][2]))
            elif k == 'ORIGIN':
                origin = (float(meta[k][0]), float(meta[k][1]), float(meta[k][2]))
            elif k == 'POINT_DATA':
                n = int(meta[k][0])
            elif k == 'SCALARS':
                if meta[k][1] == 'double':
                    # Note: Binary VTK legacy files are assumed to ALWAYS be encoded in big endian format.
                    dtype = np.dtype('>f8')
                else:
                    raise ValueError('Expected image of type double')

        print('Dimensions',dims)
        print('Spacing',spacing)
        print('Origin',origin)
        print('Num voxels',n)
        print('dtype',dtype)

        img = np.fromfile(f, dtype).astype('f8') # Read and convert to little endian
        img = img.reshape(dims[::-1]) # Reshape to the extracted dimensions
        print("IMG")
        print(img)

    np.savetxt(out_file, img.reshape(n), '%.1f', ';')
