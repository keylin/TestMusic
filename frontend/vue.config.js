const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')
const { execSync } = require('child_process')

let gitVersion = 'Unknown'
try {
  gitVersion = execSync('git log -1 --format=%cd --date=format:"%Y-%m-%d %H:%M:%S"').toString().trim()
} catch (e) {
  console.warn('Failed to get git version:', e.message)
}

module.exports = defineConfig({
  transpileDependencies: true,
  pages: {
    index: {
      entry: 'src/main.js',
      title: '歌曲管理'
    }
  },
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        'process.env.VUE_APP_VERSION': JSON.stringify(gitVersion)
      })
    ]
  }
})
