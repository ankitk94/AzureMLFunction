import numpy as np

import azureml.core
from azureml.core import Workspace

# check core SDK version number
print("Azure ML SDK Version: ", azureml.core.VERSION)

# load workspace configuration from the config.json file in the current folder.
ws = Workspace.from_config()
print(ws.name, ws.location, ws.resource_group, sep='\t')

from azureml.core import Experiment
experiment_name = 'sklearn-mnist'

exp = Experiment(workspace=ws, name=experiment_name)

# Create a compute

from azureml.core.compute import AmlCompute
from azureml.core.compute import ComputeTarget
import os

# choose a name for your cluster
compute_name = os.environ.get("AML_COMPUTE_CLUSTER_NAME", "cpucluster")
compute_min_nodes = os.environ.get("AML_COMPUTE_CLUSTER_MIN_NODES", 0)
compute_max_nodes = os.environ.get("AML_COMPUTE_CLUSTER_MAX_NODES", 4)

# This example uses CPU VM. For using GPU VM, set SKU to STANDARD_NC6
vm_size = os.environ.get("AML_COMPUTE_CLUSTER_SKU", "STANDARD_D2_V2")


if compute_name in ws.compute_targets:
    compute_target = ws.compute_targets[compute_name]
    if compute_target and type(compute_target) is AmlCompute:
        print('found compute target. just use it. ' + compute_name)
else:
    print('creating a new compute target...')
    provisioning_config = AmlCompute.provisioning_configuration(vm_size=vm_size,
                                                                min_nodes=compute_min_nodes,
                                                                max_nodes=compute_max_nodes)

    # create the cluster
    compute_target = ComputeTarget.create(
        ws, compute_name, provisioning_config)

    # can poll for a minimum number of nodes and for a specific timeout.
    # if no min node count is provided it will use the scale settings for the cluster
    compute_target.wait_for_completion(
        show_output=True, min_node_count=None, timeout_in_minutes=20)

    # For a more detailed view of current AmlCompute status, use get_status()
    print(compute_target.get_status().serialize())



from azureml.core.dataset import Dataset
data_folder = os.path.join(os.getcwd(), 'Data')
paths = [
    os.path.join(data_folder, "test-images.gz"),
    os.path.join(data_folder, "test-labels.gz"),
    os.path.join(data_folder, "train-images.gz"),
    os.path.join(data_folder, "train-labels.gz")
    ]

datastore = ws.get_default_datastore()
datastore.upload(src_dir=data_folder, target_path='mnist', overwrite=True, show_progress=True)


datastore_paths = [
    (datastore, "test-images.gz"),
    (datastore, "test-labels.gz"),
    (datastore, "train-images.gz"),
    (datastore, "train-labels.gz"),
]
dataset = Dataset.File.from_files(path = datastore_paths)

from azureml.core.environment import Environment
from azureml.core.conda_dependencies import CondaDependencies

env = Environment('my_env')
cd = CondaDependencies.create(pip_packages=['azureml-sdk','scikit-learn','azureml-dataprep[pandas,fuse]>=1.1.14'])
env.python.conda_dependencies = cd

from azureml.train.sklearn import SKLearn

script_params = {
    '--data-folder': dataset.as_named_input('mnist').as_mount(),
    '--regularization': 0.5
}

script_folder = os.path.join(os.getcwd(), "scripts")

est = SKLearn(source_directory=script_folder,
              script_params=script_params,
              compute_target=compute_target,
              environment_definition=env, 
              entry_script='train.py')


run = exp.submit(config=est)
run