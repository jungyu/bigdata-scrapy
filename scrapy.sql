/* CREATE SCHEMA `scrapy` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; */

CREATE TABLE `scrapy`.`crawler_article` (
  `id` bigint(40) NOT NULL AUTO_INCREMENT,
  `list_id` bigint(30) DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `source_url` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `source_available` tinyint(1) DEFAULT NULL,
  `source_content` mediumtext COLLATE utf8mb4_general_ci,
  `source_media` text COLLATE utf8mb4_general_ci,
  `source_modified` int(10) DEFAULT NULL,
  `content` mediumtext COLLATE utf8mb4_general_ci,
  `media` text COLLATE utf8mb4_general_ci,
  `target_table` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `target_id` bigint(40) DEFAULT NULL,
  `created` int(10) DEFAULT NULL,
  `modified` int(10) DEFAULT NULL,
  `last_source_sync` int(10) DEFAULT NULL,
  `last_target_sync` int(10) DEFAULT NULL,
  `available` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`crawler_articlemeta` (
  `id` bigint(50) NOT NULL AUTO_INCREMENT,
  `article_id` bigint(40) DEFAULT NULL,
  `meta_key` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `meta_value` text COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`crawler_fields` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `source_id` bigint(20) DEFAULT NULL,
  `source_fields` text COLLATE utf8mb4_general_ci,
  `target_fields` text COLLATE utf8mb4_general_ci,
  `created` int(10) DEFAULT NULL,
  `available` tinyint(1) DEFAULT NULL,
  `version` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`crawler_list` (
  `id` bigint(30) NOT NULL AUTO_INCREMENT,
  `source_id` bigint(20) DEFAULT NULL,
  `topic` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `article_title` text COLLATE utf8mb4_general_ci,
  `article_url` text COLLATE utf8mb4_general_ci,
  `created` int(10) DEFAULT NULL,
  `modified` int(10) DEFAULT NULL,
  `last_sync` int(10) DEFAULT NULL,
  `available` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`crawler_media` (
  `id` bigint(50) NOT NULL AUTO_INCREMENT,
  `article_id` bigint(40) DEFAULT NULL,
  `articlemeta_id` bigint(50) DEFAULT NULL,
  `media_name` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `media_type` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `media_content` longblob,
  `created` int(10) DEFAULT NULL,
  `modified` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`crawler_source` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(90) DEFAULT NULL,
  `description` text,
  `topics` text,
  `source_domain` varchar(200) DEFAULT NULL,
  `crawler_url` varchar(200) DEFAULT NULL,
  `crawler_schema` text,
  `created` int(10) DEFAULT NULL,
  `modified` int(10) DEFAULT NULL,
  `schedule_sync` int(10) DEFAULT NULL,
  `last_sync` int(10) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`wp_postmeta` (
  `meta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `post_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `meta_key` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `meta_value` longtext COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`meta_id`),
  KEY `post_id` (`post_id`),
  KEY `meta_key` (`meta_key`(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`wp_posts` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `post_author` bigint(20) unsigned NOT NULL DEFAULT '0',
  `post_date` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `post_date_gmt` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `post_content` longtext COLLATE utf8mb4_general_ci NOT NULL,
  `post_title` text COLLATE utf8mb4_general_ci NOT NULL,
  `post_excerpt` text COLLATE utf8mb4_general_ci NOT NULL,
  `post_status` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'publish',
  `comment_status` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'open',
  `ping_status` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'open',
  `post_password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `post_name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `to_ping` text COLLATE utf8mb4_general_ci NOT NULL,
  `pinged` text COLLATE utf8mb4_general_ci NOT NULL,
  `post_modified` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `post_modified_gmt` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `post_content_filtered` longtext COLLATE utf8mb4_general_ci NOT NULL,
  `post_parent` bigint(20) unsigned NOT NULL DEFAULT '0',
  `guid` varchar(255) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `menu_order` int(11) NOT NULL DEFAULT '0',
  `post_type` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'post',
  `post_mime_type` varchar(100) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `comment_count` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  KEY `post_name` (`post_name`(191)),
  KEY `type_status_date` (`post_type`,`post_status`,`post_date`,`ID`),
  KEY `post_parent` (`post_parent`),
  KEY `post_author` (`post_author`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`wp_term_relationships` (
  `object_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `term_taxonomy_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `term_order` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`object_id`,`term_taxonomy_id`),
  KEY `term_taxonomy_id` (`term_taxonomy_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`wp_term_taxonomy` (
  `term_taxonomy_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `term_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `taxonomy` varchar(32) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `description` longtext COLLATE utf8mb4_general_ci NOT NULL,
  `parent` bigint(20) unsigned NOT NULL DEFAULT '0',
  `count` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`term_taxonomy_id`),
  UNIQUE KEY `term_id_taxonomy` (`term_id`,`taxonomy`),
  KEY `taxonomy` (`taxonomy`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`wp_termmeta` (
  `meta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `term_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `meta_key` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `meta_value` longtext COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`meta_id`),
  KEY `term_id` (`term_id`),
  KEY `meta_key` (`meta_key`(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `scrapy`.`wp_terms` (
  `term_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `slug` varchar(200) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `term_group` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`term_id`),
  KEY `slug` (`slug`(191)),
  KEY `name` (`name`(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


INSERT INTO `scrapy`.`crawler_source`
(`name`,
`description`,
`topics`,
`source_domain`,
`crawler_url`,
`crawler_schema`,
`created`,
`modified`,
`schedule_sync`,
`last_sync`,
`enabled`)
VALUES
('ToScrape', NULL, 'books', 'http://books.toscrape.com', 'http://books.toscrape.com', '{"allowed_domain":["www.gvm.com.tw"],"allow":"article/","extractor_link":"//div[@class=\"article-list-item__intro\"]/a[1]","extractor_next":"//*[@class=\"fa fa-chevron-right\"]/ancestor::a","xpath_exists":"//h1/text()","xpath_title":"//h1/text()","xpath_image":"//figure[@class=\"pc-article-pic-full\"]/img/@src","xpath_description":"//section[@class=\"article-content\"]"}', NULL, NULL, NULL, NULL, NULL);

INSERT INTO `scrapy`.`crawler_fields`
(
`source_id`,
`source_fields`,
`target_fields`)
VALUES
(
1,
'{"xpath_author":"//div[@class=\"pc-bigArticle\"]/a/text()","xpath_author_url":"//div[@class=\"pc-bigArticle\"]/a/@href","xpath_title":"//article[@class=\"pc-bigArticle\"]//h1","xpath_abstract":"//meta[@name=\"description\"]/@content","xpath_subtitles":"//section[@class=\"article-content\"]/h3/text()","xpath_content":"//section[@class=\"article-content\"]","xpath_terms":"","xpath_tags":"//ul[@class=\"BreadCrumbs\"]/li/a/text()","xpath_publish_date":"//div[@class=\"article-time\"]/text()","xpath_images":"//section[@class=\"article-content\"]//img/@src","xpath_images_alter":"//section[@class=\"article-content\"]//img/@alt","xpath_images_caption":"//section[@class=\"article-content\"]//img/following-sibling::span[@class=\"article-figcaption\"]","image_url_prefix":"","terms_ignore_indexs":"","tags_ignore_indexs":"1"}',
'{"wp_posts":{"article":{"post_date":"xpath_publish_date","post_content":"xpath_content","post_title":"xpath_title","post_excerpt":"xpath_abstract"},"images":{"post_date":"xpath_publish_date","post_title":"xpath_images_alter","post_excerpt":"xpath_images_caption"}},"wp_postmea":{"author_name":"xpath_author","author_url":"xpath_author_url","subtitles":"xpath_subtitles"},"wp_terms":{"tags":{"name":"xpath_tags"},"terms":{"name":"xpath_terms"}}}'
);
