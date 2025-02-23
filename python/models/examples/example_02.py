"""
Example model. This script creates a 200 x 200 x 3 mm plate made of 1100 aluminum alloy. Four transducers are created,
demonstrating the different excitation-modes ('top', 'bot', 'asymmetric', 'symmetric'). Also, a 12 mm through-hole is
added. Two load cases with different excitation signals are created. The plate is discretized with 16 elements per
wavelength in-plane and 8 elements per thickness out-of-plane.
"""


from guwlib import *
import numpy as np

# constants ------------------------------------------------------------------------------------------------------------
PLATE_WIDTH = 0.2
PLATE_LENGTH = 0.2
PLATE_THICKNESS = 3e-3
PHASED_ARRAY_N_ELEMENTS = 4
PHASED_ARRAY_RADIUS = 0.25 * PLATE_WIDTH


class Model(FEModel):
    def setup_parameters(self):
        # basic simulation parameters ----------------------------------------------------------------------------------
        self.max_frequency = 300e3
        self.elements_per_wavelength = 16
        self.elements_in_thickness_direction = 8
        self.model_approach = 'point_force'

        # setup plate, defects and transducers -------------------------------------------------------------------------
        aluminum = IsotropicMaterial(material_name='AluminumAlloy1100')

        self.plate = IsotropicRectangularPlate(material=aluminum,
                                               thickness=3e-3,
                                               width=PLATE_WIDTH,
                                               length=PLATE_LENGTH)

        phased_array = []
        phi = np.linspace(0, 2 * np.pi, PHASED_ARRAY_N_ELEMENTS + 1)
        pos_x = PLATE_WIDTH / 2 + PHASED_ARRAY_RADIUS * np.cos(phi[0:-1])
        pos_y = PLATE_LENGTH / 2 + PHASED_ARRAY_RADIUS * np.sin(phi[0:-1])
        position_z_values = ['top', 'bottom', 'symmetric', 'asymmetric']

        for i, (x, y) in enumerate(zip(pos_x, pos_y)):
            phased_array.append(CircularTransducer(position_x=x,
                                                   position_y=y,
                                                   position_z=position_z_values[i % 4],
                                                   diameter=16e-3))

        self.defects = [Hole(position_x=15e-2, position_y=3e-2, diameter=12e-3)]
        self.transducers = phased_array

        # set up the time / loading information ------------------------------------------------------------------------
        burst = Burst(center_frequency=100e3, n_cycles=3)
        dirac = DiracImpulse()

        transducer_signals_1 = [burst] * len(self.transducers)
        transducer_signals_2 = [dirac] * len(self.transducers)

        self.load_cases = [LoadCase(name='burst_step',
                                    duration=2e-5,
                                    transducer_signals=transducer_signals_1,
                                    output_request='history'),
                           LoadCase(name='dirac_step',
                                    duration=2e-5,
                                    transducer_signals=transducer_signals_2,
                                    output_request='history')]


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    Model().setup_in_abaqus()
