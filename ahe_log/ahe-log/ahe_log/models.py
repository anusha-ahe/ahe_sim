from django.db import models

LOG_LEVELS = (
    ('INFO', 'INFO'),
    ('WARNING', 'WARNING'),
    ('DEBUG', 'DEBUG'),
    ('ERROR', 'ERROR'),
    ('FATAL', 'FATAL'),
)


class EsLogger(models.Model):
    id = models.AutoField(primary_key=True)
    logger_name = models.CharField(max_length=100)
    level = models.CharField(choices=LOG_LEVELS, max_length=50)
    msg = models.TextField()
    trace = models.TextField(blank=True, null=True)
    file_name = models.CharField(blank=True, null=True, max_length=100)
    line_no = models.IntegerField()
    create_datetime = models.DateTimeField(
        auto_now_add=True, verbose_name='Created at')

    def __str__(self):
        return self.msg

    class Meta:
        ordering = ('-create_datetime',)
        db_table = 'es_logger'
        verbose_name_plural = verbose_name = 'Logging'
