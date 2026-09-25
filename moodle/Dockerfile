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

# Language packs are downloaded at build time; a failed download is not fatal.
RUN mkdir -p /opt/langpacks && for l in $LANGPACKS; do \
        curl -fsSL -o /tmp/$l.zip "https://download.moodle.org/download.php/direct/langpack/5.2/$l.zip" \
        && unzip -q /tmp/$l.zip -d /opt/langpacks && rm /tmp/$l.zip || echo "Language pack $l not downloaded"; \
    done

COPY moodle/setup_ai.php moodle/write_config.php moodle/entrypoint.sh /var/www/moodle/
RUN chmod +x /var/www/moodle/entrypoint.sh \
    && mkdir -p /var/www/moodledata && chown -R www-data:www-data /var/www/moodledata /var/www/moodle

EXPOSE 80
ENTRYPOINT ["/var/www/moodle/entrypoint.sh"]
CMD ["apache2-foreground"]
