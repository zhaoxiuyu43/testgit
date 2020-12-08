diff --git a/ds_adapter.c b/ds_adapter.c
index d8a8b64..9140be7 100644
--- a/ds_adapter.c
+++ b/ds_adapter.c
@@ -147,6 +147,8 @@ void ds_upload_ids(){
     DataMsg_t msg;
     memset(&msg,0,sizeof(DataMsg_t));
     msg.msg_id = DATA_CMD_UPLOAD_TODAY_IDS;
+    msg.flag = MSG_HAS_DATA;
+    msg.msg_data = buf;
     msg.flag |= MSG_FLAG_TYPE_MASK;
     dc_xQueueSend(g_dc_ctrl.receive_queue,&msg,100,false);
 }
@@ -812,6 +814,13 @@ void ds_send_stock_list(StockSymbol_List *list){
         for(uint8_t index = 0;index < list->list_count; index++){
             len += strlen(list->list[index].symbol)+1;
         }
+     if(fd_st<0){
+        fd_st = file_open(ST_LOG_NAME,FILE_OPEN_W_FROM_END);
+        if(fd_st<0){
+            DC_LOG_INFO("startStlog first open fail\n");
+            core_dump();
+            return;
+        }
         out_buffer = dc_mem_alloc(len);
         memset(out_buffer,0,len);
         uint8_t *position = out_buffer;
@@ -1922,41 +1931,3 @@ void startApStlog(){
 
 #endif
 
-
-#ifdef DEBUG_FS_DATA
-#define DS_DATA_START_ADDR       (0x08160000)
-#define DS_DATA_END_ADDR         (0x08200000)
-#define ST_FLASH_PAGE_SIZE       4096
-
-void 1dumpFile(uint8_t *filename, 
-uint16_t datalen){
-    DC_LOG_INFO("dumpFile() %s\n",filename);
-    int fd=0;
-    int readsize=0;
-    struct file_stat stat = {0};
-    fd = file_open(filename,FILE_OPEN_R);
-    if(fd < 0){
-        DC_LOG_ERROR("dumpFile() open file error\n");
-        return;
-    }
-    file_lstat(filename,&stat);
-    uint32_t filesize = stat.st_size;
-    DC_LOG_INFO("dumpFile() file size %d\n",filesize);
-    char *buff= pvPortMalloc(ST_FLASH_PAGE_SIZE);
-    for(int i=0;i<(filesize/ST_FLASH_PAGE_SIZE+1);i++){
-        readsize = file_read(fd, buff, ST_FLASH_PAGE_SIZE);
-        DC_LOG_INFO("dumpFile readsize %d\n",readsize);
-        if(readsize==0)
-            memset(buff,0x00,ST_FLASH_PAGE_SIZE);
-        if((DS_DATA_START_ADDR+i*ST_FLASH_PAGE_SIZE)>=DS_DATA_END_ADDR){
-            DC_LOG_INFO("No space left\n");
-            break;
-        }
-        eraseFlashPages(DS_DATA_START_ADDR+i*ST_FLASH_PAGE_SIZE,DS_DATA_START_ADDR+i*ST_FLASH_PAGE_SIZE+ST_FLASH_PAGE_SIZE);
-        writeFlashchar(DS_DATA_START_ADDR+i*ST_FLASH_PAGE_SIZE,buff,ST_FLASH_PAGE_SIZE);
-    }
-    vPortFree(buff);
-    file_close(fd);
-
-#endif
-
