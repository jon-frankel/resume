import path from 'path';
import { fileURLToPath } from 'url';
import webpack from "webpack";
import devServer from 'webpack-dev-server';

const __filename = fileURLToPath(import.meta.url); // get the resolved path to the file
const __dirname = path.dirname(__filename); // get the name of the directory

console.log("Received LAMBDA_URL: ", process.env.LAMBDA_URL);

const config: webpack.Configuration = {
    node: {
        __dirname: "node-module",
    },
    entry: './src/index.ts',
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
        ],
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
    },
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'public')
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env.LAMBDA_URL': JSON.stringify(process.env.LAMBDA_URL),
        }),
    ],
    devServer: {
        static: './public',
        // Note: localstack CORS config does not work with any port other than 80
        port: 80,
    },
    mode: 'production',
};

export default config;
