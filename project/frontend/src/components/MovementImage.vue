<template>
  <div class="movement-img">
    <img :src="currentImage" :alt="name" loading="lazy" />
    <span class="movement-label">{{ name }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
})

const IMAGES = {
  neckFlex: '/movements/neck-flex.jpg',
  neckSide: '/movements/neck-side.jpg',
  neckRotate: '/movements/neck-rotate.jpg',
  neckIso: '/movements/neck-isometric.jpg',
  neckFull: '/movements/neck-full.jpg',
  shoulder: '/movements/shoulder-circle.jpg',
  scapula: '/movements/scapular-squeeze.jpg',
  upperBack: '/movements/upper-back.jpg',
  chest: '/movements/chest-open.jpg',
  catCowSeated: '/movements/cat-cow-seated.jpg',
  catCow: '/movements/cat-cow.jpg',
  twist: '/movements/seated-twist.jpg',
  forwardFold: '/movements/forward-fold.jpg',
  pelvic: '/movements/pelvic-tilt.jpg',
  sideBend: '/movements/side-bend.jpg',
  bridge: '/movements/glute-bridge.jpg',
  child: '/movements/child-pose.jpg',
  breath: '/movements/breath.jpg',
  wallAngel: '/movements/wall-angel.jpg',
  birdDog: '/movements/bird-dog.jpg',
  deadBug: '/movements/dead-bug.jpg',
  standing: '/movements/standing-stretch.jpg',
}

function pickImage(name) {
  const n = name.toLowerCase()
  if (n.includes('颈')) {
    if (n.includes('等长')) return 'neckIso'
    if (n.includes('前屈后伸')) return 'neckFlex'
    if (n.includes('侧屈')) return 'neckSide'
    if (n.includes('全方位') || n.includes('活动')) return 'neckFull'
    if (n.includes('环绕') || n.includes('旋转')) return 'neckRotate'
  }
  if (n.includes('靠墙')) return 'wallAngel'
  if (n.includes('鸟狗')) return 'birdDog'
  if (n.includes('死虫')) return 'deadBug'
  if (n.includes('肩胛')) return 'scapula'
  if (n.includes('上背')) return 'upperBack'
  if (n.includes('胸部') || n.includes('开合')) return 'chest'
  if (n.includes('猫牛')) return n.includes('坐姿') ? 'catCowSeated' : 'catCow'
  if (n.includes('骨盆')) return 'pelvic'
  if (n.includes('臀桥')) return 'bridge'
  if (n.includes('婴儿')) return 'child'
  if (n.includes('呼吸')) return 'breath'
  if (n.includes('扭转')) return 'twist'
  if (n.includes('前屈')) return 'forwardFold'
  if (n.includes('侧弯') || n.includes('侧腰') || n.includes('侧屈')) return 'sideBend'
  if (n.includes('环绕')) return 'shoulder'
  if (n.includes('肩')) return 'shoulder'
  return 'standing'
}

const currentImage = computed(() => IMAGES[pickImage(props.name)] || IMAGES.standing)
</script>

<style scoped>
.movement-img {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.movement-img img {
  width: 100%;
  max-width: 160px;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: 8px;
  background: #f8f9fa;
}
.movement-label {
  font-size: 11px;
  color: #999;
}
@media (min-width: 768px) {
  .movement-img img { max-width: 200px; }
  .movement-label { font-size: 13px; }
}
</style>
