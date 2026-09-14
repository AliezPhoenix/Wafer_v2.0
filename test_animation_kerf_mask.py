"""动画已切刀痕：5px、0.75 透明同色掩膜，细线压在上面。"""
import unittest

import numpy as np

from Functions import Animation_Y_POS

BLUE = np.array([255, 255, 51], dtype=np.uint8)
YELLOW = np.array([0, 255, 255], dtype=np.uint8)


def wafer(y_pos, current_sp=(-1, -1), current_x=200, if_cut=0):
    img, _ = Animation_Y_POS(
        (980, 980), y_pos, list(current_sp), current_x, 0, 1, if_cut, "Square", 1.0)
    return img[:, :1000]


class TestKerfMask(unittest.TestCase):
    def test_blue_completed_mask_under_line(self):
        img = wafer([[0, 0, 0, 0, 0, 1]])
        np.testing.assert_allclose(img[500, 400], BLUE, atol=2)
        expected = (BLUE * 0.75).astype(np.uint8)
        np.testing.assert_allclose(img[502, 400], expected, atol=8)

    def test_yellow_completed_mask_under_line(self):
        img = wafer([[0, 0, 0, 0, 0, 2]])
        np.testing.assert_allclose(img[500, 400], YELLOW, atol=2)
        expected = (YELLOW * 0.75).astype(np.uint8)
        np.testing.assert_allclose(img[502, 400], expected, atol=8)

    def test_uncut_has_no_mask(self):
        img = wafer([[0, 0, 0, 0, 0, 0]])
        np.testing.assert_allclose(img[500, 400], [255, 255, 255], atol=2)
        np.testing.assert_allclose(img[502, 400], [0, 0, 0], atol=2)

    def test_current_cut_path_has_no_completed_mask(self):
        img = wafer([[0, 0, 0, 0, 0, 0]], current_sp=(0, -1), current_x=200, if_cut=1)
        np.testing.assert_allclose(img[502, 400], [0, 0, 0], atol=2)


if __name__ == "__main__":
    unittest.main()
