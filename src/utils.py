import os
import os.path as osp
import torch_geometric.transforms as T
from torch_geometric.data import DataLoader
from src.data_loader import OurDataset


def get_comment(data_nativeness, data_compression, data_type,
                lr, batch_size, local_feature_combo, global_features,
                target_class, log_descr=False):

    comment = f'\nData nativeness: {data_nativeness}\n' \
              f'Data compression: {data_compression}\n' \
              f'Data type: {data_type}\n' \
              f'Local features: {local_feature_combo}\n' \
              f'Global features: {global_features}\n' \
              f'\n' \
              f'Learning rate: {lr}\n' \
              f'Batch size: {batch_size}\n'

    if log_descr == True:
        # 0. Save to log_record.txt
        comment = data_nativeness + '  ' + data_compression + "  " + data_type + '  ' \
                    + "LR=" + str(lr) + '\t\t' \
                    + "Batch=" + str(batch_size) + '\t\t' \
                    + "Local features:" + str(local_feature_combo) + '\t\t' \
                    + "Global features:" + str(global_features) + '\t\t' \
                    + "Data used: " + data_compression + '_' + data_type + '\t\t' \
                    + "Split class: " + target_class

    return comment



def get_id(prefix=''):
    '''
    :return: The next expected id number of an experiment
             that hasn't yet been recorded!
    '''
    with open(f'logs/LOG_{prefix}.txt', 'r') as log_record:
        next_id = len(log_record.readlines()) + 1

    return str(next_id)

def save_to_log(experiment_description, prefix=''):
    '''
    Saves the experiment description into the log
    :param experiment_description: all the variables in a nice format
    '''

    # If the log file does not exist - create it
    add_first_line = False
    if not os.path.exists(f'logs/LOG_{prefix}.txt'):
        add_first_line = True

    if add_first_line:
        with open(f'logs/LOG_{prefix}.txt', 'w+') as log_record:
            log_record.write(f'LOG OF ALL THE EXPERIMENTS for {prefix}')

    with open(f'logs/LOG_{prefix}.txt', 'a+') as log_record:
        next_id = get_id(prefix=prefix)
        log_record.write('\n#{} ::: {}'.format(next_id, experiment_description))


import itertools


def get_grid_search_local_features(local_feats):
    '''
    Return all permutations of parameters passed
    :return: [ [], [cortical], [myelin], ..., [cortical, myelin], ... ]
    '''

    # 1. Get all permutations of local features
    local_fs = [[], ]
    for l in range(1, len(local_feats) + 1):
        for i in itertools.combinations(local_feats, l):
            local_fs.append(list(i))

    return local_fs


def get_data_path(data_nativeness, data_compression, data_type, hemisphere='left'):

    '''
    Returns the correct path to files

    data_nativeness: {'native', 'aligned'}
    data_compression: {'50', '90'}
    data_type: {'inflated', 'pial', 'midthickness', 'sphere', 'veryinflated', 'white'}
    hemisphere: {'left', 'right'}

    Eg.
    data_folder = '/vol/biomedic/users/aa16914/shared/data/dhcp_neonatal_brain/surface_fsavg32k/reduced_50/vtk/pial'
    data_folder = '/vol/biomedic/users/aa16914/shared/data/dhcp_neonatal_brain/surface_native/reduced_50/inflated/vtk'
    files_ending = '_hemi-L_pial_reduce50.vtk'
    files_ending = '_left_inflated_reduce50.vtk'
    '''

    root = '/vol/biomedic/users/aa16914/shared/data/dhcp_neonatal_brain/'

    data_nativeness_paths = {'native': 'surface_native/',
                             'aligned': 'surface_fsavg32k/'}

    data_compression_paths = {'50': 'reduced_50/',
                              50: 'reduced_50/',
                              '90': 'reduced_90/',
                              90: 'reduced_90/',
                              'original': 'original32k/'}

    data_type_paths = {'inflated': 'inflated/',
                       'pial': 'pial/',
                       'midthickness': 'midthickness/',
                       'sphere': 'sphere/',
                       'veryinflated': 'veryinflated/',
                       'white': 'white/'}

    hemisphere_paths = {'left_native_original': f'_left_{data_type}.vtk',
                        'left_native_50':       f'_left_{data_type}_reduce50.vtk',
                        'left_native_90':       f'_left_{data_type}_reduce90.vtk',

                        'right_native_original': f'_right_{data_type}.vtk',
                        'right_native_50':       f'_right_{data_type}_reduce50.vtk',
                        'right_native_90':       f'_right_{data_type}_reduce90.vtk',


                        'left_aligned_original': f'_hemi-L_{data_type}.vtk',
                        'left_aligned_50':       f'_hemi-L_{data_type}_reduce50.vtk',
                        'left_aligned_90':       f'_hemi-L_{data_type}_reduce90.vtk',

                        'right_aligned_original': f'_hemi-R_{data_type}.vtk',
                        'right_aligned_50':       f'_hemi-R_{data_type}_reduce50.vtk',
                        'right_aligned_90':       f'_hemi-R_{data_type}_reduce90.vtk'}

    if data_nativeness == 'native':

        data_folder = root + data_nativeness_paths[data_nativeness] + data_compression_paths[data_compression] + data_type_paths[data_type] + 'vtk'
        files_ending = hemisphere_paths[hemisphere + f'_{data_nativeness}_{data_compression}']

        return data_folder, files_ending

    elif data_nativeness == 'aligned':

        data_folder = root + data_nativeness_paths[data_nativeness] + data_compression_paths[data_compression] + 'vtk/' + data_type_paths[data_type][:-1]
        files_ending = hemisphere_paths[hemisphere + f'_{data_nativeness}_{data_compression}']

        return data_folder, files_ending



def data(data_folder, files_ending, data_type, target_class, task, REPROCESS, local_features, global_features, indices, batch_size, num_workers=2):
    '''
    Get data loaders and data sets

    :param data_folder:
    :param files_ending:
    :param data_type:
    :param target_class:
    :param task:
    :param REPROCESS:
    :param local_features:
    :param global_features:
    :param indices:
    :param batch_size:
    :param num_workers:
    :return:
    '''

    path = osp.join(
        osp.dirname(osp.realpath(__file__)), '..', 'data/' + target_class + f'/Reduced50/{data_type}')

    # Transformations
    transform = T.Compose([
        # T.RandomTranslate(0.1),
        # T.RandomFlip(0, p=0.3),
        # T.RandomFlip(1, p=0.1),
        # T.RandomFlip(2, p=0.3),
        T.FixedPoints(16247),
        T.RandomRotate(360, axis=0),
        T.RandomRotate(360, axis=1),
        T.RandomRotate(360, axis=2)
    ])

    pre_transform = T.NormalizeScale()

    train_dataset = OurDataset(path, train=True, transform=transform, pre_transform=pre_transform,
                               target_class=target_class, task=task, reprocess=REPROCESS,
                               local_features=local_features, global_feature=global_features,
                               val=False, indices=indices['Train'],
                               data_folder=data_folder,
                               files_ending=files_ending)

    test_dataset = OurDataset(path, train=False, transform=transform, pre_transform=pre_transform,
                              target_class=target_class, task=task, reprocess=REPROCESS,
                              local_features=local_features, global_feature=global_features,
                              val=False, indices=indices['Test'],
                              data_folder=data_folder,
                              files_ending=files_ending)

    validation_dataset = OurDataset(path, train=False, transform=transform, pre_transform=pre_transform,
                                    target_class=target_class, task=task, reprocess=REPROCESS,
                                    local_features=local_features, global_feature=global_features,
                                    val=True, indices=indices['Val'],
                                    data_folder=data_folder,
                                    files_ending=files_ending)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    val_loader = DataLoader(validation_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    return train_dataset, test_dataset, validation_dataset, train_loader, test_loader, val_loader



if __name__ == '__main__':
    pass
     # # Model Parameters
    # lr = 0.001
    # batch_size = 8
    # num_workers = 2
    #
    # local_features = ['corr_thickness', 'myelin_map', 'curvature', 'sulc']
    # global_features = None
    # target_class = 'gender'
    # task = 'segmentation'
    # # number_of_points = 12000
    #
    # test_size = 0.09
    # val_size = 0.1
    # reprocess = False
    #
    # data = "reduced_50"
    # type_data = "inflated"
    #
    # log_descr = "LR=" + str(lr) + '\t\t'\
    #           + "Batch=" + str(batch_size) + '\t\t'\
    #           + "Num Workers=" + str(num_workers) + '\t'\
    #           + "Local features:" + str(local_features) + '\t'\
    #           + "Global features:" + str(global_features) + '\t'\
    #           + "Data used: " + data + '_' + type_data + '\t'\
    #           + "Split class: " + target_class
    #
    # save_to_log(log_descr)