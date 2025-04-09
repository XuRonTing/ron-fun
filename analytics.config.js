// 数据埋点SDK统一配置

export default {
  // Google Analytics配置
  ga: {
    trackingId: 'UA-XXXXX-Y',
    debug: process.env.NODE_ENV !== 'production',
    anonymizeIp: true
  },

  // Mixpanel配置
  mixpanel: {
    token: 'mp_xxxxxxxxxxxx',
    persistence: 'localStorage',
    trackPageview: true
  },

  // 自定义事件映射
  events: {
    BUTTON_CLICK: 'button_click',
    PAGE_VIEW: 'page_view',
    SCROLL_DEPTH: 'scroll_depth',
    TIME_SPENT: 'time_spent'
  }
}