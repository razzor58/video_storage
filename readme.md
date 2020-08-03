#### Приложение видео-архив

Для запуска в локальном кластере
```
kubectl apply -f ./k8s
```
Открыть в браузере
```
http://localhost:1337
```

Ограничения на загрузку видео:
 - Поддерживаются только прямые ссылки на файлы, которые отдают в ответе массив байтов, например
   https://gitlab.com/razzor58/video-storage/-/raw/master/sample_video.mov?inline=false
    
    
Ways to improve:
 - Error handling
 - Tests
 - Celery task chain 
 - Add flower service
 - Async download from link
 - CI in GKE
 