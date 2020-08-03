#### Приложение видео-архив

Выполнить локально
```
docker-compose up -d
```
Открыть в браузере
```
http://localhost:1337
```

Ограничения на загрузку видео:
 - Поддерживается только ссылка прямая ссылка по корой в ответ возвращается непосредственно 
    массив байтов, например
    https://gitlab.com/razzor58/video-storage/-/raw/master/sample_video.mov?inline=false
    
    
TODO:
 - Celery task chain 
 - Add flower service
 - Async link download
 - Error handling
 - Tests
 - CI in GKE
 