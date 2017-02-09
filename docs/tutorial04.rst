Step 2
======
At this stage we need to input the failure rate data. We need to provide aging parameters (:math:`N_0` and :math:`A`) and the Age of each pipe (link) at the time of analysis.

RRPAM-WDS facilitates input of aging parameters based on asset groups. Let's assume two groups of pipes. Following are the aging parameters estimated for each group. The last column gives the cost of replacement for a km of pipe in terms of millions of financial units.

+-----------------------+--------------------+---------------+---------------+
|  Diameter Range       | :math:`N_0`        | :math:`A`     |Cost (millions)|
+=======================+====================+===============+===============+
| :math:`d\ \leq` 80 mm | 0.120              | 0.0185        | 700           |
+-----------------------+--------------------+---------------+---------------+
| 80 mm :math:`\gt\ d`  | 0.081              | 0.0136        | 1000          |
+-----------------------+----------------------+-------------+-+-------------+

Go to the :strong:`Asset Data` window and select and select :strong:`Property Groups` tab,  Change the number of groups to 2 and enter the above values.

.. figure:: images/asset_data1.PNG
   :scale: 100 %
   :alt: EPANET 2.0 network files can have junctions with no coordinates.

Now the next step is to assign each pipe to one of these two groups. Go to the :strong:`Assign Assets` tab on the :strong:`Asset Data` (same) window. 
