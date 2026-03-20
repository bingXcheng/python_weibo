/*
Navicat MySQL Data Transfer

Source Server         : 8.28
Source Server Version : 80011
Source Host           : localhost:3306
Source Database       : weiboarticle

Target Server Type    : MYSQL
Target Server Version : 80011
File Encoding         : 65001
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `article`
-- ----------------------------
DROP TABLE IF EXISTS `article`;
CREATE TABLE `article` (
  `id` bigint(20) DEFAULT NULL,
  `likeNum` bigint(20) DEFAULT NULL,
  `commentsLen` bigint(20) DEFAULT NULL,
  `reposts_count` bigint(20) DEFAULT NULL,
  `region` text,
  `content` text,
  `contentLen` bigint(20) DEFAULT NULL,
  `created_at` text,
  `type` text,
  `detailUrl` text,
  `authorAvatar` text,
  `authorName` text,
  `authorDetail` text,
  `isVip` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) DEFAULT NULL COMMENT '用户ID',
  `screen_name` text COMMENT '用户昵称',
  `followers_count` text COMMENT '粉丝数',
  `verified` int(11) DEFAULT 0 COMMENT '是否认证',
  `sentiment` float DEFAULT NULL COMMENT '情感值 0-1',
  `sentiment_label` text DEFAULT NULL COMMENT '正面/中性/负面'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Table structure for `comments`
-- ----------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `articleId` text,
  `created_at` text,
  `like_counts` text,
  `region` text,
  `content` text,
  `authorName` text,
  `authorGender` text,
  `authorAddress` text,
  `authorAvatar` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` text,
  `password` text,
  `createTime` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Table structure for `sentiment_cache`
-- ----------------------------
DROP TABLE IF EXISTS `sentiment_cache`;
CREATE TABLE `sentiment_cache` (
  `id` int AUTO_INCREMENT PRIMARY KEY,
  `text_hash` bigint(20) UNIQUE COMMENT '文本hash避免重复计算',
  `text` text COMMENT '原文(截取前500字)',
  `sentiment` float COMMENT '情感值',
  `sentiment_label` text COMMENT '情感标签',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
