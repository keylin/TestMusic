<template>
  <el-container style="margin: 0; min-height: 100vh;">
    <el-main style="max-width: 800px; margin: 0 auto; padding-top: 50px;">
      
      <h1 class="text-center title">我的歌单</h1>
      
      <!-- Input Section -->
      <el-row justify="center" @submit.prevent="fetchLinkDetails" style="margin-top: 40px;">
        <el-col :span="24">
          <el-form-item>
            <div style="display: flex; width: 100%;">
              <el-input v-model="state.link" size="large"
                        placeholder="输入歌单链接 (支持网易云/QQ音乐/汽水音乐)"
                        @keyup.enter="throttledFetchLinkDetails"
                        class="custom-input">
              </el-input>
              <el-button type="danger" size="large" 
                         @click="throttledFetchLinkDetails" 
                         :loading="state.loading" 
                         class="custom-button">
                获取歌单
              </el-button>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- Options Section -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="8">
           <el-form-item label="格式:">
            <el-select v-model="state.songFormat" placeholder="选择格式" size="default">
              <el-option label="歌名 - 歌手" value="song-singer" />
              <el-option label="歌手 - 歌名" value="singer-song" />
              <el-option label="仅歌名" value="song" />
            </el-select>
           </el-form-item>
        </el-col>
        <el-col :span="8">
           <el-form-item label="顺序:">
             <el-select v-model="state.songOrder" placeholder="选择顺序" size="default">
              <el-option label="正序" value="normal" />
              <el-option label="倒序" value="reverse" />
            </el-select>
           </el-form-item>
        </el-col>
        <el-col :span="8" style="display: flex; align-items: center;">
           <el-checkbox v-model="state.useDetailedSongName">保留原始歌名</el-checkbox>
            <el-tooltip content="不勾选通常能获得更好的跨平台匹配率" placement="top">
              <el-icon class="info-icon"><InfoFilled/></el-icon>
            </el-tooltip>
        </el-col>
      </el-row>

      <!-- Result Section -->
      <transition name="el-fade-in-linear">
        <div v-if="state.result || state.songsCount > 0">
           <el-divider content-position="center">解析结果 (共 {{ state.songsCount }} 首)</el-divider>
           
           <el-input type="textarea" v-model="state.result" :rows="15" placeholder="解析结果将显示在这里..."></el-input>
           
           <div style="margin-top: 20px; text-align: center;">
             <el-button type="primary" size="large" @click="copyResult">一键复制</el-button>
             <el-button type="success" size="large" @click="downloadExcel" style="margin-left: 10px;">下载表格</el-button>
           </div>
        </div>
      </transition>

    </el-main>
  </el-container>
</template>

<script setup>
import { reactive } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { InfoFilled } from '@element-plus/icons-vue';

// State
const state = reactive({
  link: '',
  result: '',
  songsCount: 0,
  useDetailedSongName: false,
  songFormat: 'song-singer',
  songOrder: 'normal',
  loading: false,
});

// Utils
const isValidUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch (e) {
    return false;
  }
};

const throttle = (fn, delay) => {
  let lastTime = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastTime >= delay) {
      fn.apply(this, args);
      lastTime = now;
    }
  };
};

const reset = (msg, type = 'error') => {
  if (msg) ElMessage[type](msg);
  state.loading = false;
};

// Actions
const fetchLinkDetails = async () => {
  const link = state.link.trim();
  if (!link) {
    reset('请输入歌单链接', 'warning');
    return;
  }
  
  if (!isValidUrl(link)) {
    reset('链接格式无效', 'error');
    return;
  }

  state.loading = true;
  state.result = '';
  state.songsCount = 0;

  const params = new URLSearchParams();
  params.append('url', link);

  try {
    const queryParams = `?detailed=${state.useDetailedSongName}&format=${state.songFormat}&order=${state.songOrder}`;
    
    // Relative path call
    const resp = await axios.post('/songlist' + queryParams, params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    if (resp.data.code !== 1) {
      reset(resp.data.msg || '获取失败，请稍后重试');
      return;
    }

    const { songs, songs_count } = resp.data.data;
    if (!songs || songs.length === 0) {
      reset('未找到歌曲，请检查链接是否正确或歌单是否公开');
      return;
    }

    state.result = songs.join('\n');
    state.songsCount = songs_count;
    state.loading = false;
    ElMessage.success('解析成功');

  } catch (err) {
    console.error(err);
    const msg = err.response?.data?.msg || '网络请求请求失败';
    reset(msg);
  }
};

const throttledFetchLinkDetails = throttle(fetchLinkDetails, 1000);

const copyResult = () => {
  if (!state.result) {
    ElMessage.warning('没有内容可复制');
    return;
  }
  navigator.clipboard.writeText(state.result).then(() => {
    ElMessage.success('已复制到剪贴板');
  }).catch(() => {
    // Fallback
    const textarea = document.createElement('textarea');
    textarea.value = state.result;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    ElMessage.success('已复制到剪贴板');
  });
};

const downloadExcel = async () => {
  if (!state.result) {
    ElMessage.warning('没有内容可下载');
    return;
  }
  
  try {
    const songs = state.result.split('\n');
    const resp = await axios.post('/export/excel', { songs }, {
      responseType: 'blob'
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'songlist.xlsx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
  } catch (err) {
    console.error(err);
    ElMessage.error('下载失败');
  }
};
</script>

<style>
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
  background-color: #f5f7fa;
}

.title {
  color: #409EFF;
  margin-bottom: 30px;
  font-weight: bold;
}

.text-center {
  text-align: center;
}

.info-icon {
  margin-left: 5px;
  color: #909399;
  cursor: help;
  vertical-align: middle;
}

.custom-input .el-input__wrapper {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.custom-button {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}
</style>