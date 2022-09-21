from biobb_common.tools import test_fixtures as fx
from biobb_cp2k.cp2k.cp2k_run import cp2k_run

class TestCp2kRun():
    def setup_class(self):
        fx.test_setup(self, 'cp2k_run')

    def teardown_class(self):
        fx.test_teardown(self)
        pass

    def test_cp2k_run(self):
        cp2k_run(properties=self.properties, **self.paths)
        assert fx.not_empty(self.paths['output_log_path'])
        assert fx.not_empty(self.paths['output_outzip_path'])
        assert fx.not_empty(self.paths['output_rst_path'])
