from __future__ import annotations
from _utils_import import np, torch

def get_translate_matrix(x, y, z):
    return np.array([
        [1., 0., 0., x],
        [0., 1., 0., y],
        [0., 0., 1., z],
        [0., 0., 0., 1.]
    ])


def get_rotation_matrix_euler(euler_x_degree=None, euler_y_degree=None, euler_z_degree=None, euler_x_radian=None, euler_y_radian=None, euler_z_radian=None):
    if euler_x_degree is not None:
        euler_x_radian = np.deg2rad(euler_x_degree)
    if euler_y_degree is not None:
        euler_y_radian = np.deg2rad(euler_y_degree)
    if euler_z_degree is not None:
        euler_z_radian = np.deg2rad(euler_z_degree)

    if euler_x_radian is not None:
        rot_x = np.array([
            [1., 0.,                     0.,                      0.],
            [0., np.cos(euler_x_radian), -np.sin(euler_x_radian), 0.],
            [0., np.sin(euler_x_radian), np.cos(euler_x_radian),  0.],
            [0., 0.,                     0.,                      1.]
        ])
        return rot_x
    elif euler_y_radian is not None:
        rot_y = np.array([
            [np.cos(euler_y_radian),  0., np.sin(euler_y_radian), 0.],
            [0.,                      1., 0.,                     0.],
            [-np.sin(euler_y_radian), 0., np.cos(euler_y_radian), 0.],
            [0.,                      0., 0.,                     1.]
        ])
        return rot_y
    elif euler_z_radian is not None:
        rot_z = np.array([
            [np.cos(euler_z_radian), -np.sin(euler_z_radian), 0., 0.],
            [np.sin(euler_z_radian), np.cos(euler_z_radian),  0., 0.],
            [0.,                     0.,                      1., 0.],
            [0.,                     0.,                      0., 1.]
        ])
        return rot_z
    else:
        raise ValueError("At least one of euler_x_degree, euler_y_degree, or euler_z_degree must be provided")



# adapted from smplx.lbs.batch_rodrigues
def axis_angle_to_rotation_matrix_batch(
    rot_vecs: torch.Tensor,
    epsilon: float = 1e-8,
) -> torch.Tensor:
    ''' Calculates the rotation matrices for a batch of rotation vectors
        Parameters
        ----------
        rot_vecs: torch.tensor Nx3
            array of N axis-angle vectors
        Returns
        -------
        R: torch.tensor Nx3x3
            The rotation matrices for the given axis-angle parameters
    '''

    batch_size = rot_vecs.shape[0]
    device, dtype = rot_vecs.device, rot_vecs.dtype

    angle = torch.norm(rot_vecs + 1e-8, dim=1, keepdim=True)
    rot_dir = rot_vecs / angle

    cos = torch.unsqueeze(torch.cos(angle), dim=1)
    sin = torch.unsqueeze(torch.sin(angle), dim=1)

    # Bx1 arrays
    rx, ry, rz = torch.split(rot_dir, 1, dim=1)
    K = torch.zeros((batch_size, 3, 3), dtype=dtype, device=device)

    zeros = torch.zeros((batch_size, 1), dtype=dtype, device=device)
    K = torch.cat([zeros, -rz, ry, rz, zeros, -rx, -ry, rx, zeros], dim=1) \
        .view((batch_size, 3, 3))

    ident = torch.eye(3, dtype=dtype, device=device).unsqueeze(dim=0)
    rot_mat = ident + sin * K + (1 - cos) * torch.bmm(K, K)
    return rot_mat
