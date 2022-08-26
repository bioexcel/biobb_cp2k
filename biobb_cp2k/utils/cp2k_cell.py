""" Cell functions for package biobb_cp2k """

def get_centroid(in_pdb):

    num = 0
    sum_x = 0.0
    sum_y = 0.0
    sum_z = 0.0
    for line in open(in_pdb):
        # ATOM      2  C7  JZ4     1      21.520 -27.270  -4.230  1.00  0.00
        if line[0:4] == 'ATOM' or line[0:6] == 'HETATM':
            #atom = line[12:16]
            elem = line[77]
            x = line[30:38]
            y = line[38:46]
            z = line[46:54]
            sum_x = sum_x + float(x)
            sum_y = sum_y + float(y)
            sum_z = sum_z + float(z)
            num = num + 1

    cen_x = 0
    cen_y = 0
    cen_z = 0

    if num:
        cen_x = sum_x / num
        cen_y = sum_y / num
        cen_z = sum_z / num

        cen_x = float(f'{cen_x:.3f}')
        cen_y = float(f'{cen_y:.3f}')
        cen_z = float(f'{cen_z:.3f}')

    return cen_x, cen_y, cen_z

