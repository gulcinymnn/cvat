
# Copyright (C) 2020 Intel Corporation
#
# SPDX-License-Identifier: MIT

from accuracy_checker.data_reader import DataRepresentation
from accuracy_checker.utils import extract_image_representations


class AcLauncher(Launcher):
    @staticmethod
    def from_config(self, config):
        return __class__.from_launcher(ac.make_launcher(config))

    def __init__(self, launcher, adapter, preproc=None, postproc=None):
        self._launcher = launcher
        self._adapter = adapter
        self._preproc = preproc
        self._postproc = postproc

    def launch(self, inputs):
        batch = [DataRepresentation(i) for i in inputs]
        inputs = self._input_feeder.fill_inputs(batch)
        _, batch_meta = extract_image_representations(inputs)
        if self._preproc:
            inputs = self._preproc.process(inputs)

        outputs = self._launcher.predict(inputs, batch_meta)
        outputs = self._adapter.process(outputs, [''] * len(batch), batch_meta)

        if self._postproc:
            outputs = self._postproc.process(outputs)

        return self._convert_outputs(outputs)

    def get_categories(self):
        return self._adapter.get_categories()

    def preferred_input_size(self):
        if self.input_shape is None:
            return None

        _, _, h, w = self.input_shape
        return (h, w)

    @property
    def input_shape(self):
        if not hasattr(self, '_input_shape'):
            # Heuristic to determine input shape - use the max input shape
            self._input_shape = max(self._launcher.inputs.values(),
                defult=None, key=lambda s: abs(np.prod(s)))
        return self._input_shape

    @staticmethod
    def _convert_outputs(predictions):
        # Convert Accuracy checker predictions to Datumaro annotations
