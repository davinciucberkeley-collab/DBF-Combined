Worst case over kd / nom / hi corners, zeta 0.3 % and 1 %, thrust scale 0.77 / 1.0 / 1.25 (36 loops per row). GM = factor on the loop gain before the first closed-loop pole crosses into the right half plane (1.00 = already unstable somewhere);
PM and crossover at zeta 1 %, thrust x1.0, worst corner. `unstable` counts the loops (of 18 per axis and IMU position) with a right-half-plane pole.

| settings | axis | IMU at | min GM | unstable loops of 18 | rigid PM deg | crossover Hz |
|---|---|---|---|---|---|---|
| A.param before (P .25 / D .004 / FLTD 32, gyro 40) | pit | spar centre | 1.00 | 4 | 50 | 3.9 |
| A.param before (P .25 / D .004 / FLTD 32, gyro 40) | pit | cage hub | 1.00 | 4 | 50 | 3.8 |
| A.param before (P .25 / D .004 / FLTD 32, gyro 40) | rll | spar centre | 2.44 | 0 | 62 | 2.2 |
| A.param before (P .25 / D .004 / FLTD 32, gyro 40) | rll | cage hub | 1.00 | 17 | - | - |
| A.param before (P .25 / D .004 / FLTD 32, gyro 40) | yaw | spar centre | 1.97 | 0 | 33 | 1.5 |
| A.param before (P .25 / D .004 / FLTD 32, gyro 40) | yaw | cage hub | 1.00 | 15 | 34 | 1.5 |
| A.param now (pit .15 / .002 / 40, roll .20 / .003 / 32, yaw as before, gyro 60) | pit | spar centre | 2.76 | 0 | 56 | 2.6 |
| A.param now (pit .15 / .002 / 40, roll .20 / .003 / 32, yaw as before, gyro 60) | pit | cage hub | 3.22 | 0 | 56 | 2.6 |
| A.param now (pit .15 / .002 / 40, roll .20 / .003 / 32, yaw as before, gyro 60) | rll | spar centre | 2.52 | 0 | 64 | 1.8 |
| A.param now (pit .15 / .002 / 40, roll .20 / .003 / 32, yaw as before, gyro 60) | rll | cage hub | 1.00 | 12 | 64 | 1.8 |
| A.param now (pit .15 / .002 / 40, roll .20 / .003 / 32, yaw as before, gyro 60) | yaw | spar centre | 2.06 | 0 | 34 | 1.5 |
| A.param now (pit .15 / .002 / 40, roll .20 / .003 / 32, yaw as before, gyro 60) | yaw | cage hub | 1.00 | 15 | 35 | 1.5 |