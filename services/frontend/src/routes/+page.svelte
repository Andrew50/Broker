<script>
    import  Header  from './header.svelte';
</script>
<Header />
<main class="main-container">
  <div class="content">
    <h1 class="title" style="font-size: 32px;">EdgeFinder</h1>
    <!-- Add more content about services here -->
  </div>
</main>
<style>
    @import "../global.css";
  .main-container {
    top: 10vh;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 90vh;
    position: absolute;
    left: 0;
    right: 0;
    background-color: var(--c2); /* Example background color */
  }
  h1 {
    font-size: 24px;
    color: var(--f1);
  }

  /* Adjust styles below as needed */
  .content {
    text-align: center;
  }
</style>
