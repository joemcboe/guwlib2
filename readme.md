# GUWlib
A python package to simulate Guided Ultrasonic Wave (GUW) propagation and defect interaction in simple plates using ABAQUS. Please refer to the documentation on GitLab pages: [GUWlib documentation](https://guw-j-froboese-7e83bff35047dd42a62d8fb269d632ab5d9e6a1d5b2d7867.gitlab-pages.rz.tu-bs.de/index.html).

## Description
<!--- Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors. --->

- [ ] rectangular plates


<!--- ## Visuals --->
<!--- Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method. --->


## Installation and dependencies
No installation required. To work with GUWlib, it is only necessary to copy this repository into a local working directory.
Basic external requirements for solving FE models locally:
- [ ] ABAQUS 2019 (or later)
- [ ] Python 3 and [NumPy](https://numpy.org/) (for batch processing handlers)

The project includes additional functions for the batch processing of FE models on the [Phoenix cluster TU Braunschweig](https://doku.rz.tu-bs.de/doku.php?id=hlr:phoenix). In order to use these, additional dependencies must be satisfied:
- [ ] user account for the Phoenix cluster
- [ ] (VPN) connection to the TU BS network
- [ ] Python packages: [paramiko](https://www.paramiko.org/) (for SSH connections)

This project is tested on Windows 10 and CentOS Linux 7.3 with ABAQUS 2019 Academic Research and ABAQUS 2017 Learning Edition. 
<!--- Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection. --->

## Example usage
<!--- Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README. --->

```
from guwlib import *


class Model(FEModel):
    def setup_parameters(self):
        # basic simulation parameters
        self.max_frequency = 300e3
        self.elements_per_wavelength = 16
        self.elements_in_thickness_direction = 8
        self.model_approach = 'point_force'

        # setup plate
        aluminum = IsotropicMaterial(material_name='AluminumAlloy1100')
        self.plate = IsotropicRectangularPlate(material=aluminum, thickness=3e-3,
                                               width=0.2, length=0.2)

        # setup two transducers
        self.transducers.append(CircularTransducer(position_x=x, position_y=y, position_z='symmetric',
                                                   diameter=16e-3))
        self.transducers.append(CircularTransducer(position_x=x, position_y=y, position_z='symmetric',
                                                   diameter=16e-3))

        # setup defects
        self.defects = [Crack(position_x=2e-2, position_y=4e-2, length=10e-3, angle_degrees=0),
                        Hole(position_x=15e-2, position_y=3e-2, diameter=12e-3)]

        # set up the time / loading information (burst on 1st transducer)
        burst = Burst(center_frequency=100e3, n_cycles=3)
        transducer_signals = [burst, None]
        self.load_cases = [LoadCase(name='control_step', duration=0.25e-3,
                                    transducer_signals=transducer_signals, output_request='field')]


if __name__ == "__main__":
    Model().setup_in_abaqus()
```

Running this script in ABAQUS will setup the following FE model:



## Project status
<!--- If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers. -->

This project is no longer maintained from 02/2024. Some features are currently not fully integrated or need revision:
- [ ] Piezo-electric transducers, which require an implicit solver (at least for the piezo-electric part of the model). 
    The option of building the model with piezo-electrical transducers is implemented in principle, however, the bottom-level
    ABAQUS/Python API code is not up-to-date with the rest of the project.
- [ ] The helper function for field-output export is not fully integrated.

The modular structure should make it easy to add features. A few inspirations for what could be added with little to moderate effort are:
- [ ] Option to specify the solver and element type. Currently, the solver is always set to ABAQUS/Explicit and element type is always set
    to ``C3D8R``.
- [ ] Option to implement the excitation as a prescribed nodal displacement (currently, excitation is always realized as a concentrated force).
- [ ] Options to specify the interval with which field output is written to the output database. Currently, 
    field output is written at intervals of 10 * maximum theoretical time increment.
- [ ] More options to request field output for a load case. Currently, users can only request field output for the 
    top surface of the plate, but not for e.g. the whole plate.
- [ ] Anisotropic material for the plate.
- [ ] More types of defects. 
- [ ] Non-rectangular or polygon-shaped plates.
- [ ] Multi-layered anisotropic plates.


<!---
    ```mermaid
    classDiagram
        note "note 01"
        note for model "test\ntest\ntest"
        steps --|> model : time data
        plate --|> model : spatial data
        class model{
            - max_frequency
            - model_mode
            - nodes_per_wavelength
            - elements_in_thickness_direction
            setup_in_abaqus()
        }
        class steps{
        }
        class plate{
        }
    ```
--->
