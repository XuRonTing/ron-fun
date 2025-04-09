// postcss配置文件
module.exports = {
  plugins: {
    'postcss-px-to-viewport': {
      viewportWidth: 375, // 设计稿宽度（iPhone13）
      unitPrecision: 5, // 转换保留小数位数
      viewportUnit: 'vw', // 转换单位
      selectorBlackList: ['.ignore'], // 忽略类名
      minPixelValue: 1, // 最小转换值
      mediaQuery: false, // 媒体查询不转换
      include: /\/src\// // 只转换src目录
    }
  }
}