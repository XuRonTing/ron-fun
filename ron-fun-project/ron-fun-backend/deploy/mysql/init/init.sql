-- 初始化MySQL数据库脚本
-- 创建用于Ron.fun项目的初始数据

-- 确保使用UTF-8编码
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建超级管理员账号
INSERT INTO `user` (`username`, `email`, `hashed_password`, `is_active`, `is_superuser`, `nickname`, `avatar`, `bio`, `points`, `total_points`, `used_points`, `created_at`, `updated_at`)
VALUES
('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 1, 1, '系统管理员', 'https://ui-avatars.com/api/?name=Admin', '系统管理员账号', 0, 0, 0, NOW(), NOW());

-- 初始化商品分类
INSERT INTO `product_category` (`name`, `description`, `icon`, `created_at`, `updated_at`)
VALUES
('电子产品', '各类电子数码产品', 'https://cdn.example.com/icons/electronics.png', NOW(), NOW()),
('生活用品', '日常生活必需品', 'https://cdn.example.com/icons/daily.png', NOW(), NOW()),
('礼品卡', '各类礼品卡和代金券', 'https://cdn.example.com/icons/giftcard.png', NOW(), NOW());

-- 初始化Banner位置
INSERT INTO `banner` (`title`, `description`, `image_url`, `link_type`, `link_url`, `is_active`, `sort_order`, `position`, `created_at`, `updated_at`)
VALUES
('欢迎使用Ron.fun', '一站式积分兑换平台', 'https://cdn.example.com/banners/welcome.jpg', 'url', 'https://example.com/welcome', 1, 1, 'home_top', NOW(), NOW()),
('每日签到赚积分', '连续签到奖励更多', 'https://cdn.example.com/banners/signin.jpg', 'url', 'https://example.com/signin', 1, 2, 'home_top', NOW(), NOW());

-- 初始化应用列表
INSERT INTO `application` (`name`, `description`, `icon`, `link_type`, `link_url`, `is_active`, `sort_order`, `position`, `created_at`, `updated_at`)
VALUES
('每日签到', '每日签到领取积分', 'https://cdn.example.com/icons/signin.png', 'url', 'https://example.com/signin', 1, 1, 'home_app', NOW(), NOW()),
('幸运抽奖', '使用积分参与抽奖', 'https://cdn.example.com/icons/lottery.png', 'url', 'https://example.com/lottery', 1, 2, 'home_app', NOW(), NOW()),
('积分商城', '使用积分兑换商品', 'https://cdn.example.com/icons/shop.png', 'url', 'https://example.com/shop', 1, 3, 'home_app', NOW(), NOW()),
('分享赚积分', '邀请好友获得积分', 'https://cdn.example.com/icons/share.png', 'url', 'https://example.com/share', 1, 4, 'home_app', NOW(), NOW());

-- 初始化抽奖类型
INSERT INTO `lottery_type` (`name`, `code`, `description`, `icon`, `created_at`, `updated_at`)
VALUES
('九宫格抽奖', 'grid', '经典九宫格抽奖', 'https://cdn.example.com/lottery/grid.png', NOW(), NOW()),
('幸运大转盘', 'wheel', '转盘式抽奖', 'https://cdn.example.com/lottery/wheel.png', NOW(), NOW());

SET FOREIGN_KEY_CHECKS = 1; 