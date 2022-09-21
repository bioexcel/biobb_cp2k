from biobb_common.tools import test_fixtures as fx
from biobb_cp2k.cp2k.cp2k_prep import cp2k_prep

class TestCp2kPrep():
    def setup_class(self):
        fx.test_setup(self, 'cp2k_prep')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_cp2k_prep(self):
        cp2k_prep(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_inp_path'])
        assert fx.equal(self.paths['output_inp_path'], self.paths['ref_output_inp_path'])
