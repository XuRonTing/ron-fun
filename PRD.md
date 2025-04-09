# 产品需求文档

## 前端页面功能模块

### 技术选型
- 前端框架：React 18 + TypeScript
- 后端语言：python 3.12
- 构建工具：Vite 4
- UI组件库：@headlessui/react + heroicons
- 状态管理：Zustand
- 路由方案：React Router 6
- 请求库：axios 1.6
- 移动端适配：postcss-px-to-viewport
- 动效库：framer-motion

### 云服务器
- 云服务器：阿里云ECS
- 服务器操作系统：Ubuntu 22.04 64位
- 服务器公网IP：106.14.251.109
- 服务器登录名称：root
- 服务器登录密码：WZxrt17302134750
- 服务器域名解析：www.rongting.fun

### 云数据库
- 云数据库：阿里云RDS
- 云数据库名称：rm-uf65k8k5p79dlesl6
- 云数据库类型：MySQL 8.0
- 云数据库网络类型：专有网络 vpc-uf62fpqum4a6w8tqt0yaj

### 1. 核心页面结构
- 路由层级：
  - 一级路由：/login（登录）、/main（主布局）
  - 二级路由：/main/profile（个人中心）、/main/lottery（抽奖）、/main/shop（商城）
- 页面组件：
  - AuthGuard：路由守卫组件（登录状态校验）
  - ResponsiveLayout：响应式布局容器（支持移动端折叠菜单）

### 2. 组件交互规范
- 全局弹窗规范：
  - 使用@headlessui/react对话框组件
  - 动效过渡时长300ms（fade-in-up）
- 表单提交规范：
  - 防抖处理（500ms）
  - 错误提示统一使用Toast组件

### 3. 移动端适配方案
- 断点配置：
  - ≥768px：桌面布局
  - 480-767px：平板布局
  - ≤479px：移动端布局
- PostCSS配置：
  - 视口基准：375px（基于iPhone13）
  - 单位精度：保留5位小数
  - 包含文件：./src/**/*.{jsx,tsx,less}
  - 排除范围：/node_modules/
  - 媒体查询：不转换media query中的px单位
  - 视口单位：vw

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    'postcss-px-to-viewport': {
      viewportWidth: 375, // iOS基准（iPhone13）
      androidViewportWidth: 360, // 安卓基准（360dp）
      unitPrecision: 5,
      viewportUnit: 'vw',
      selectorBlackList: ['.ignore'],
      minPixelValue: 1,
      mediaQuery: false,
      include: /\/src\//
    }
  }
}
```
- 特殊适配：
  - 九宫格抽奖采用vw单位适配
  - 滑动操作支持touch事件

### 4. 用户状态同步
- 状态更新策略：
  - 积分变动使用SWR库自动刷新
  - 跨标签页同步：监听storage事件
- 心跳机制：
  - 每5分钟检测登录态
  - 过期前15分钟弹出续期弹窗
- 路由配置：
  - /login 登录页
  - /profile 个人中心
  - /lottery 九宫格抽奖
  - /shop 积分商城
- 页面容器组件：
  - 全局导航栏（含用户状态展示）
  - 移动端响应式布局容器

### 2. 交互规范
- 表单验证：
  - 登录/注册表单实时校验
  - 积分修改二次确认弹窗
- 状态管理：
  - Redux维护用户登录态
  - LocalStorage持久化关键数据

### 3. 移动端适配方案
- 视口配置：`<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">`
- 布局方案：
  - 主内容区采用CSS Grid布局
  - 抽奖九宫格使用aspect-ratio:1保持正方形
  - 商城商品列表使用CSS多列布局（column-count）
- 手势支持：
  - 左滑右滑切换Tab页（使用react-use-gesture库）
  - 长按触发商品详情（持续时间800ms）

### 4. 用户状态同步
- WebSocket实时更新积分变动
- 全局loading状态统一管理

## 后台管理系统功能模块

### 1. 用户管理
- 用户列表展示（账号、昵称、积分、身份状态）
- 支持修改用户身份（普通用户/管理员）
- 积分调整功能
- 账号状态控制（启用/禁用）

### 2. 积分商城管理
- 商品列表展示（商品图、名称、所需积分）
- 商品新增/编辑（包含上下架状态）
- 积分兑换记录查询

### 3. 应用管理
- 应用列表展示（应用图标、名称、版本）
- 应用信息新增/编辑
- 应用状态维护

### 4. Banner管理
- Banner轮播图配置
- Banner排序与时效设置
- Banner点击数据统计

## 交互流程
1. 登录/注册流程（包含状态保持）
2. 用户信息修改流程
3. 商品上下架审批流程

### 4. 积分兑换失败补偿流程
- **失败触发条件**：
  - 网络异常（HTTP状态码5xx/请求超时）
  - 库存不足（API返回错误码INSUFFICIENT_STOCK）
- **自动重试机制**：
  - 阶梯式重试（10s/30s/60s）最多3次
  - 重试期间展示进度提示Toast
- **补偿规则**：
  - 重试成功：立即发放商品并扣减积分
  - 最终失败：24小时内自动返还积分至账户

流程图说明：
```
[用户发起兑换] → [库存/网络检查] → 成功 → 完成兑换
                ↓ 失败
                → [自动重试机制]（3次） → 成功 → 完成兑换
                                    ↓ 最终失败
                                    → [积分自动返还] + [显示备选方案]
```

## 数据统计模块

### 埋点方案
- 事件类型映射表：
  | 事件名称          | 事件代码示例                                  | 触发场景                |
  |-------------------|---------------------------------------------|-----------------------|
  | 兑换按钮点击       | trackEvent('shop_convert_click')             | 商城页兑换操作时触发    |
  | 抽奖按钮点击       | trackEvent('lottery_trigger_click')          | 抽奖页发起抽奖时触发    |
  | 个人资料修改       | trackEvent('profile_update_success')         | 用户信息更新成功时触发  |

- 实施方式：
  1. **关键事件手动埋点**
    - 按钮点击：`trackEvent('button_click', { element: '兑换按钮', page: '/shop' })`
    - 页面跳转：在React Router的导航守卫中添加`trackPageView`
  2. **自动行为追踪**
    - 停留时长：使用`useEffect`监听路由变化记录时间差
    - 滚动深度：监听`window.scroll`事件计算可视区域占比
  3. **banner点击数据统计**
    - 记录banner点击事件：`trackEvent('banner_click', { banner_id: '12345' })`
    - 统计banner点击次数：`trackPageView('/banner/12345')`
  4. **应用点击数据统计**
    - 记录应用点击事件：`trackEvent('app_click', { app_id: '12345' })`
    - 统计应用点击次数：`trackPageView('/app/12345')`
  5. **用户登录状态同步**
    - 记录用户登录事件：`trackEvent('user_login', { user_id: '12345' })`
    - 统计用户登录次数：`trackPageView('/user/12345')`


### SDK配置规范
```javascript
// analytics.config.js
export default {
  ga: {
    trackingId: 'UA-XXXXX-Y',
    debug: process.env.NODE_ENV !== 'production'
  },
  mixpanel: {
    token: 'mp_xxxxxxxxxxxx',
    persistence: 'localStorage'
  }
}
```

## 权限体系
- 普通用户：仅查看基础信息
- 管理员：具备全部管理权限

## 原型参考
![未登录状态]UI/未登录状态.png  
![已登录状态]UI/已登录状态.png  
![用户管理]后台管理列表/管理后台-用户管理.png
![用户积分修改]后台管理列表/管理后台-用户管理-修改积分.png
![用户身份修改]后台管理列表/管理后台-用户管理-修改身份.png
![积分商城]后台管理列表/管理后台-积分商城.png
![商品新增]后台管理列表/管理后台-积分商城-新增商品.png
![商品编辑]后台管理列表/管理后台-积分商城-编辑商品.png
![应用管理]后台管理列表/管理后台-应用管理.png
![应用新增]后台管理列表/管理后台-应用管理-新增应用.png
![Banner管理]后台管理列表/管理后台-Banner管理.png
![新增banner]后台管理列表/管理后台-Banner管理-新增banner.png
![编辑banner]后台管理列表/管理后台-Banner管理-编辑banner.png

## 前端原型示意图
![登录流程]UI/登录页.png  
![个人中心]UI/用户个人信息详情页--编辑.png  
![抽奖交互]UI/九宫格抽奖弹窗.png  
![商城弹窗]UI/兑换积分商城商品的弹窗.png
![大转盘交互]UI/大转盘游戏.png
![用户信息状态]UI/用户个人信息详情页--只读.png
![用户信息编辑]UI/用户个人信息详情页--编辑.png
![密码修改]UI/用户个人信息详情页--修改密码.png
![已登录状态]H5的前端UI/已登录状态.png
![未登录状态]H5的前端UI/未登录状态.png



# 数据库表结构：
## 数据统计模块

### 埋点方案
- 事件类型映射表：
  | 事件名称          | 事件代码示例                                  | 触发场景                |
  |-------------------|---------------------------------------------|-----------------------|
  | 兑换按钮点击       | trackEvent('shop_convert_click')             | 商城页兑换操作时触发    |
  | 抽奖按钮点击       | trackEvent('lottery_trigger_click')          | 抽奖页发起抽奖时触发    |
  | 个人资料修改       | trackEvent('profile_update_success')         | 用户信息更新成功时触发  |

- 实施方式：
  1. **关键事件手动埋点**
    - 按钮点击：`trackEvent('button_click', { element: '兑换按钮', page: '/shop' })`
    - 页面跳转：在React Router的导航守卫中添加`trackPageView`
  2. **自动行为追踪**
    - 停留时长：使用`useEffect`监听路由变化记录时间差
    - 滚动深度：监听`window.scroll`事件计算可视区域占比
  3. **第三方服务集成**
    - Google Analytics：通过gtag.js上报核心转化事件
    - Mixpanel：初始化SDK后使用`mixpanel.track()`记录用户行为

### SDK配置规范
```javascript
// analytics.config.js
export default {
  ga: {
    trackingId: 'UA-XXXXX-Y',
    debug: process.env.NODE_ENV !== 'production'
  },
  mixpanel: {
    token: 'mp_xxxxxxxxxxxx',
    persistence: 'localStorage'
  }
}
```

## 权限体系表：
- 普通用户：只允许访问H5页面，不允许访问后台管理系统
- 管理员：允许访问H5页面和后台管理系统，拥有所有权限
- 普通用户：
  - 登录/注册
  - 个人中心
  - 抽奖
  - 商城
- 管理员：
  - 登录/注册
  - 个人中心
  - 抽奖
  - 商城
  - 用户管理
  - 积分商城管理
  - 应用管理
  - Banner管理

## 数据库设计
- 用户表：
  - 字段：user_id、username、password、phone_number、Remaining_Points、​Total_Points、User_Profile_Picture、vip_level、is_admin、created_at、updated_at、user_status
    - user_id：用户ID
    - username：用户名
    - password：密码。加密存储
    - phone_number：手机号
    - Remaining_Points：剩余积分。默认值为0
    - Total_Points：总积分。默认值为0
    - User_Profile_Picture：用户头像。默认URL格式：：URL_ADDRESSting.fun/avatar/{user_id}.png
    - vip_level：VIP等级
    - is_admin：是否为管理员
    - created_at：创建时间
    - updated_at：更新时间
    - user_status：用户状态。1：正常，2：禁用


- 商品表：
  - 字段：product_id、product_name、product_introduction、product_price、product_stock、product_​ordering、product_is_on_sale、created_at、updated_at
    - product_id：商品ID
    - product_name：商品名称
    - product_introduction：商品简介
    - product_price：商品价格
    - product_stock：商品库存
    - product_ordering：商品排序，用于控制商品展示顺序
    - product_is_on_sale：商品是否上架，用于控制商品展示状态
    - created_at：创建时间
    - updated_at：更新时间


- 积分变更记录表：
  - 索引设计：
    * 联合索引(user_id, exchange_time) 用于用户积分流水查询
    * 单列索引(product_id) 用于商品兑换统计
    * 覆盖索引(user_id, reason) 用于用户行为分析
  - 字段：record_id、user_id、reason、point_number、product_id、exchange_time、created_at、updated_at
    - user_id：关联用户表的user_id，用于记录积分变更记录
    - reason：
        - 1：抽奖消耗积分
        - 2：抽奖增加积分
        - 3：兑换商品
        - 4：后台调整
    - point_number：
        - 正数：增加积分，示例：+5000
        - 负数：减少积分，示例：-2000
    - product_id：关联商品表的product_id，用于记录商品兑换记录
    - exchange_time：积分兑换时间
    - record_id：积分变更记录ID
    - created_at：创建时间
    - updated_at：更新时间


- 积分商城订单表：
  - 字段：order_id、user_id、product_id、order_status、order_time、created_at、updated_at
    - order_status：
        - 1：待支付
        - 2：已支付
        - 3：已取消
    - order_time：订单支付时间
    - order_id：订单ID
    - user_id：关联用户表的user_id，用于记录订单信息
    - product_id：关联商品表的product_id，用于记录订单信息
    - created_at：创建时间
    - updated_at：更新时间


- 应用表：
  - 字段：app_id、app_name、app_introduction、app_icon、app_link、app_​ordering、app_is_on_sale、created_at、updated_at
    - app_id：应用ID
    - app_link：应用跳转链接
    - app_ordering：应用排序，用于控制应用展示顺序
    - app_is_on_sale：应用是否上架，用于控制应用展示状态
    - app_icon：应用图标
    - app_introduction：应用简介
    - app_name：应用名称
    - created_at：创建时间
    - updated_at：更新时间


- Banner表：
  - 字段：banner_id、banner_name、banner_image、banner_link、banner_order、banner_introduction、banner_expiration、created_at、updated_at
    - banner_id：Banner ID
    - banner_name：Banner名称
    - banner_image：Banner图片
    - banner_link：Banner跳转链接
    - banner_order：Banner排序，用于控制Banner展示顺序
    - banner_introduction：Banner简介
    - banner_expiration：Banner过期时间
    - created_at：创建时间
    - updated_at：更新时间


- Banner点击记录表：
  - 字段：click_id、click_user_name、click_user_id、banner_id、click_time、created_at、updated_at
    - click_id：点击记录ID
    - banner_id：关联Banner表的banner_id，用于记录点击记录
    - click_time：点击时间
    - click_user_id：关联用户表的user_id，用于记录点击记录。如果用户未登录，则记录为null
    - click_user_name：关联用户表的username，用于记录点击记录。如果用户未登录，则记录为null
    - created_at：创建时间
    - updated_at：更新时间

- VIP等级表：
  - 字段：vip_id、vip_name、vip_icon、vip_level、vip_total_point、vip_expiration、created_at、updated_at
    - vip_id：VIP等级ID
    - vip_name：VIP等级名称。默认值为普通用户
    - vip_icon：VIP等级图标。
    - vip_level：VIP等级。默认值为0
    - vip_total_point：VIP等级所需总积分。默认值为0
    - vip_expiration：VIP等级过期时间。目前不设置过期时间，默认为null
    - created_at：创建时间
    - updated_at：更新时间


**核心流程配图**：
- 登录流程：UI/登录页.png
- 注册流程：UI/注册页.png
- 用户状态：UI/已登录状态.png
- 积分修改：后台管理列表/管理后台-用户管理-修改积分.png
- 商品新增：后台管理列表/管理后台-积分商城-新增商品.png