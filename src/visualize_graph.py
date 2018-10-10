# -*- coding: utf-8 -*-
# @Author: Yulin Liu
# @Date:   2018-10-10 14:23:23
# @Last Modified by:   Yulin Liu
# @Last Modified time: 2018-10-10 15:33:54

import numpy as np
import tensorflow as tf
import os
from configparser import ConfigParser
from rnn_encoder_decoder import LSTM_model
import matplotlib.pyplot as plt


class visual_graph:
    def __init__(self, 
                 conf_path,
                 restored_model_path):
        self.restored_model_path = restored_model_path
        self.conf_path = conf_path
        self.load_configs()
        
    def load_configs(self):
        parser = ConfigParser(os.environ)
        parser.read(self.conf_path)
        config_header = 'nn'
        self.n_input = parser.getint(config_header, 'n_input')
        self.n_channels = parser.getint('convolution', 'n_channels')
        self.n_controled_var = parser.getint('lstm', 'n_controled_var')
        self.n_encode = parser.getint(config_header, 'n_encode')
        self.state_size = parser.getint('lstm', 'n_cell_dim')
        self.n_layer = parser.getint('lstm', 'n_lstm_layers')
        # Number of contextual samples to include
        self.batch_size = parser.getint(config_header, 'batch_size')
        
    def define_placeholder(self):
        # define placeholder
        self.input_encode_tensor = tf.placeholder(dtype = tf.float32, shape = [None, None, self.n_encode], name = 'encode_tensor')
        self.seq_len_encode = tf.placeholder(dtype = tf.int32, shape = [None], name = 'seq_length_encode')
        self.input_tensor = tf.placeholder(dtype = tf.float32, shape = [None, None, self.n_input, self.n_input, self.n_channels], name = 'decode_feature_map')
        self.input_decode_coords_tensor = tf.placeholder(dtype = tf.float32, shape = [None, None, self.n_controled_var], name = 'decode_coords')
        self.target = tf.placeholder(dtype = tf.float32, shape = [None, None, self.n_controled_var], name = 'target')
        self.target_end = tf.placeholder(dtype = tf.float32, shape = [None, None, 1], name = 'target_end')
        self.target_end_neg = tf.placeholder(dtype = tf.float32, shape = [None, None, 1], name = 'target_end_neg')
        self.seq_length = tf.placeholder(dtype = tf.int32, shape = [None], name = 'seq_length_decode')
        return

    def launchGraph(self):
        self.define_placeholder()
        self.MODEL = LSTM_model(conf_path = self.conf_path,
                                batch_x = self.input_encode_tensor,
                                seq_length = self.seq_len_encode,
                                n_input = self.n_encode,
                                batch_x_decode = self.input_tensor,
                                batch_xcoords_decode = self.input_decode_coords_tensor,
                                seq_length_decode = self.seq_length,
                                n_input_decode = self.n_input,
                                target = self.target,
                                train = False,
                                weight_summary = False)
        return
    
    def restore_model(self):
        self.graph = tf.Graph()
        self.launchGraph()
        self.sess = tf.Session()
        self.saver = tf.train.Saver()
        self.saver.restore(self.sess, restored_model_path)
        self.weights = self.return_weights()
        self.sess.close()
        return
    
    def return_weights(self):
        weight_list = tf.trainable_variables()
        weights = {}
        for v in weight_list:
            weights[v.name] = self.sess.run(v)
        return weights

def visualize_weights(weight_var, fig_size = (16, 4)):
    n_layers = weight_var.shape[3]
    n_channels = weight_var.shape[2]
    fig, axs = plt.subplots(n_channels, n_layers, figsize=fig_size, facecolor='w', edgecolor='k')
    axs = axs.ravel()
    for i in range(n_channels):
        for j in range(n_layers):
            axs[n_layers * i + j].imshow(weight_var[:, :, i, j], 
                                   cmap = 'bwr',
                                   vmax = weight_var.max(), 
                                   vmin = weight_var.min())
            axs[n_layers * i + j].set_axis_off()
    plt.show()

'''
Example Code:
'''
'''
tf.reset_default_graph()
restored_model_path = 'visual_network/model.ckpt-99'
config_path = 'configs/encoder_decoder_nn.ini'
visual_graph_class = visual_graph(config_path, restored_model_path)
visual_graph_class.restore_model()
weights = visual_graph_class.weights

visualize_weights(weight_var=weights['wc1:0'], fig_size = (8, 2))
visualize_weights(weight_var=weights['wc2:0'], fig_size = (8,4))
visualize_weights(weight_var=weights['wc3:0'], fig_size = (8,4))
'''