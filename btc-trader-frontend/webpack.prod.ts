import { merge } from 'webpack-merge';
import { Configuration } from 'webpack';
import * as path from 'path';
import commonConfig from './webpack.common';

const prodConfig: Configuration = merge(commonConfig, {
    mode: 'production',
    devtool: 'source-map',
    output: {
        path: path.resolve(__dirname, 'build'),
        filename: '[name].[contenthash].js',
        publicPath: '/',
        clean: true
    },
    optimization: {
        minimize: true,
        splitChunks: {
            chunks: 'all',
            name: false
        }
    },
    performance: {
        hints: false,
        maxEntrypointSize: 512000,
        maxAssetSize: 512000
    }
});

export default prodConfig; 