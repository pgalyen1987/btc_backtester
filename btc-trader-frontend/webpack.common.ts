import path from 'path';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import { Configuration } from 'webpack';

const commonConfig: Configuration = {
    entry: './src/index.tsx',
    output: {
        path: path.resolve(__dirname, 'dist'),
        filename: '[name].[contenthash].js',
        clean: true
    },
    module: {
        rules: [
            {
                test: /\.(ts|tsx)$/,
                use: {
                    loader: 'ts-loader',
                    options: {
                        transpileOnly: true,
                        configFile: path.resolve(__dirname, 'tsconfig.json')
                    }
                },
                exclude: /node_modules/
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            },
            {
                test: /\.(png|svg|jpg|jpeg|gif|ico)$/i,
                type: 'asset/resource'
            }
        ]
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js', '.jsx'],
        alias: {
            '@': path.resolve(__dirname, 'src'),
            'components': path.resolve(__dirname, 'src/components'),
            'services': path.resolve(__dirname, 'src/services'),
            'utils': path.resolve(__dirname, 'src/utils'),
            'types': path.resolve(__dirname, 'src/types'),
            'hooks': path.resolve(__dirname, 'src/hooks'),
            'constants': path.resolve(__dirname, 'src/constants'),
            'config': path.resolve(__dirname, 'src/config'),
            'theme': path.resolve(__dirname, 'src/theme')
        },
        fallback: {
            "path": require.resolve("path-browserify"),
            "os": require.resolve("os-browserify/browser"),
            "crypto": require.resolve("crypto-browserify"),
            "stream": require.resolve("stream-browserify"),
            "buffer": require.resolve("buffer/")
        }
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './public/index.html',
            inject: true
        })
    ],
    stats: {
        errorDetails: true,
        children: true,
        logging: 'verbose',
        modules: true,
        reasons: true,
        errors: true,
        errorStack: true
    }
};

export default commonConfig; 