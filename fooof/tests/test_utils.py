"""  """

from py.test import raises
import numpy as np

from fooof.utils import overlap, group_three, trim_psd

##
##

def test_overlap():

	lst_1 = [10, 12]
	lst_2 = [8, 13]
	lst_3 = [9, 14]

	assert overlap(lst_1, lst_2)
	assert not overlap(lst_2, lst_1)
	assert not overlap(lst_2, lst_3)

def test_group_three():

	dat = [0, 1, 2, 3, 4, 5]
	assert group_three(dat) == [[0, 1, 2], [3, 4, 5]]

	with raises(ValueError):
		group_three([0, 1, 2, 3])

def test_trim_psd():
	# NOTE: fix test when desired behaviour is specified and updated.

	f_in = np.array([0., 1., 2., 3., 4., 5.])
	p_in = np.array([1., 2., 3., 4., 5., 6.])

	f_out, p_out = trim_psd(f_in, p_in, [2., 4.])

	assert np.array_equal(f_out, np.array([2., 3., 4.]))
	assert np.array_equal(p_out, np.array([3., 4., 5.]))
