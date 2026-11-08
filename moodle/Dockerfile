# WenQuest teaching engine: Moodle 5.2 + Claude / DeepSeek AI providers.
FROM php:8.3-apache

ARG MOODLE_BRANCH=MOODLE_502_STABLE
# In mainland China, set this build arg to a reachable mirror of the Moodle git repository.
ARG MOODLE_GIT=https://github.com/moodle/moodle.git
ARG LANGPACKS="zh_cn"

RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip curl ghostscript locales postgresql-client \
        libpq-dev libzip-dev libpng-dev libjpeg62-turbo-dev libfreetype6-dev libicu-dev libxml2-dev \
    && sed -i 's/# en_AU.UTF-8/en_AU.UTF-8/; s/# zh_CN.UTF-8/zh_CN.UTF-8/' /etc/locale.gen && locale-gen \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" pgsql pdo_pgsql intl zip gd soap exif opcache \
    && pecl install redis && docker-php-ext-enable redis \
    && a2enmod rewrite headers expires \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
COPY moodle/php-moodle.ini /usr/local/etc/php/conf.d/99-moodle.ini
COPY moodle/apache-moodle.conf /etc/apache2/sites-available/000-default.conf

WORKDIR /var/www/moodle
RUN git clone --depth 1 -b "$MOODLE_BRANCH" "$MOODLE_GIT" . \
    && composer install --no-dev --no-interaction --prefer-dist --classmap-authoritative \
    && rm -rf .git

# Our plugins.
COPY plugins/aiprovider_claude public/ai/provider/claude
COPY plugins/local_wenquest public/local/wenquest

# Multi-language filter for {mlang xx}...{mlang} (bilingual content created by the AI course builder).
ARG MULTILANG2_REF=0c6fc6f11b6cd8b729ce7ca261d593ba06a1cf35
RUN git clone -q https://github.com/iarenaza/moodle-filter_multilang2.git public/filter/multilang2 \
    && git -C public/filter/multilang2 checkout -q "$MULTILANG2_REF" && rm -rf public/filter/multilang2/.git

# 在线编辑 Word、Excel（第 121 轮）：OnlyOffice 的课程活动插件和作业在线提交插件（固定提交，支持 Moodle 4.5–5.3）。
# 文档服务本身是容器 docs；地址和密钥由 setup_wenquest.php 按环境变量填写。
ARG OO_MOD_REF=5cd78f0974d7f6350db386d5490042529c075706
ARG OO_ASSIGN_REF=42ea54f44bb7c9c755e4f7a5b6923aefc4d28f75
RUN git clone -q https://github.com/ONLYOFFICE/onlyoffice-moodle.git public/mod/onlyofficeeditor \
    && git -C public/mod/onlyofficeeditor checkout -q "$OO_MOD_REF" && rm -rf public/mod/onlyofficeeditor/.git \
    && git clone -q https://github.com/ONLYOFFICE/moodle-assignsubmission_onlyoffice.git public/mod/assign/submission/onlyoffice \
    && git -C public/mod/assign/submission/onlyoffice checkout -q "$OO_ASSIGN_REF" && rm -rf public/mod/assign/submission/onlyoffice/.git

# Language packs are downloaded at build time; a failed download is not fatal.
RUN mkdir -p /opt/langpacks && for l in $LANGPACKS; do \
        curl -fsSL -o /tmp/$l.zip "https://download.moodle.org/download.php/direct/langpack/5.2/$l.zip" \
        && unzip -q /tmp/$l.zip -d /opt/langpacks && rm /tmp/$l.zip || echo "Language pack $l not downloaded"; \
    done

COPY moodle/setup_ai.php moodle/setup_wenquest.php moodle/write_config.php moodle/entrypoint.sh /var/www/moodle/
RUN chmod +x /var/www/moodle/entrypoint.sh \
    && mkdir -p /var/www/moodledata && chown -R www-data:www-data /var/www/moodledata /var/www/moodle

EXPOSE 80
ENTRYPOINT ["/var/www/moodle/entrypoint.sh"]
CMD ["apache2-foreground"]
