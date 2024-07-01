const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  mode: 'development', // or 'production' for production builds
  entry: './doc_crm_frontend/src/index.js', // entry point of your application
  output: {
    path: path.resolve(__dirname, 'dist'), // output directory
    filename: 'bundle.js', // output bundle file name
    publicPath: '/', // public URL address of the output directory when referenced in a browser
  },
  resolve: {
    extensions: ['.js', '.jsx'], // file extensions to resolve
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/, // handle JavaScript and JSX files
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader', // use babel for transpiling JavaScript/JSX
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'], // babel presets
          },
        },
      },
      {
        test: /\.css$/, // handle CSS files
        use: [MiniCssExtractPlugin.loader, 'css-loader'], // extract CSS into separate files
      },
    ],
  },
  plugins: [
    new CleanWebpackPlugin(), // clean the build directory before each build
    new MiniCssExtractPlugin({ filename: 'styles.css' }), // extract CSS into a separate file
    new HtmlWebpackPlugin({
      template: './doc_crm_frontend/public/index.html', // HTML template file
      filename: 'index.html', // output HTML file (in the output.path directory)
    }),
  ],
  devServer: {
    historyApiFallback: true, // enable HTML5 History API fallback so that all routes are handled by index.html
    contentBase: path.resolve(__dirname, 'dist'), // serve static files from dist directory
    open: true, // open browser automatically when starting the development server
    port: 3000, // port number
    proxy: {
      '/api': 'http://localhost:5000', // proxy API requests to backend server
    },
  },
};
