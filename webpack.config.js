const path = require('path');
const webpack = require('webpack');
const autoprefixer = require('autoprefixer');

const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
const BundleTracker = require('webpack-bundle-tracker');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const SentryCliPlugin = require('@sentry/webpack-plugin');
const { VueLoaderPlugin } = require('vue-loader');
var LodashModuleReplacementPlugin = require('lodash-webpack-plugin');


const devMode = process.env.NODE_ENV !== 'production';
const hotReload = process.env.HOT_RELOAD === '1';

const vueRule = {
  test: /\.vue$/,
  use: 'vue-loader',
  include: path.resolve('./static/src/js'),
  exclude: /node_modules/
};

const styleRule = {
  test: /\.(sa|sc|c)ss$/,
  use: [
    MiniCssExtractPlugin.loader,
    { loader: 'css-loader', options: { sourceMap: true } },
    { loader: 'postcss-loader', options: { plugins: () => [autoprefixer({ browsers: ['last 2 versions'] })] } },
    'sass-loader'
  ]
};

const jsRule = {
  test: /\.js$/,
  use: {
    loader: 'babel-loader',
    options: {
      presets: ['@babel/preset-env'],
      plugins: ['@babel/plugin-proposal-object-rest-spread']
    }
  },
  include: path.resolve('./static/src/js'),
  exclude: /node_modules/
};

const assetRule = {
  test: /.(jpg|png|woff(2)?|eot|ttf|svg)$/,
  loader: 'file-loader'
};

const plugins = [
  new BundleTracker({ filename: 'webpack-stats.json', path: path.resolve(__dirname, './static/dist/') }),
  new webpack.ProvidePlugin({
    $: "jquery",
    jQuery: "jquery"
  }),
  new VueLoaderPlugin(),
  new MiniCssExtractPlugin({
    filename: devMode ? '[name].css' : '[name].[hash].css',
    chunkFilename: devMode ? '[id].css' : '[id].[hash].css'
  }),
  new BundleAnalyzerPlugin({ analyzerMode: 'static', openAnalyzer: false }),
  new webpack.HotModuleReplacementPlugin(),
  new CleanWebpackPlugin(),
  new CopyWebpackPlugin({
    patterns: [
      { from: './static/src/images/**/*', to: path.resolve('./static/dist/images/[name].[ext]'), toType: 'template' }
    ]
  }),
  new LodashModuleReplacementPlugin({
    'collections': true,
    'paths': true
  })
];

if (devMode) {
  styleRule.use = ['css-hot-loader', ...styleRule.use];
} else {
  plugins.push(
    new webpack.EnvironmentPlugin(['NODE_ENV', 'RAVEN_JS_DSN', 'SENTRY_ENVIRONMENT', 'SOURCE_VERSION'])
  );
  if (process.env.SENTRY_DSN) {
    plugins.push(
      new SentryCliPlugin({
        include: '.',
        release: process.env.SOURCE_VERSION,
        ignore: ['node_modules', 'webpack.config.js'],
      })
    );
  }
}


module.exports = {
  entry: {
    main: path.join(__dirname, './static/src/js/index.js'),
    flower: path.join(__dirname, './static/src/js/flower.js'),
    filter: path.join(__dirname, './static/src/js/filter.js')
  },
  output: {
    path: path.resolve(__dirname, './static/dist/'),
    filename: '[name]-[hash].js',
    // publicPath: hotReload ? 'http://localhost:8080/' : ''
  },
  devtool: devMode ? 'cheap-eval-source-map' : 'source-map',
  devServer: {
    hot: true,
    quiet: false,
    headers: { 'Access-Control-Allow-Origin': '*' },
    writeToDisk: true
  },
  module: { rules: [vueRule, jsRule, styleRule, assetRule] },
  // externals: { jquery: 'jQuery', Sentry: 'Sentry' },
  plugins,
  optimization: {
    // minimizer: [
    //   new UglifyJsPlugin({
    //     cache: true,
    //     parallel: true,
    //     sourceMap: true // set to true if you want JS source maps
    //   }),
    //   new OptimizeCSSAssetsPlugin({})
    // ],
    splitChunks: {
      cacheGroups: {
        commons: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'initial',
        },
      }
    }
  },
};