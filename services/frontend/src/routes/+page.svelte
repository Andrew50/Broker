<script>
    import  Header  from './header.svelte';
</script>
<Header />
<main class="main-container">
  <div class="content">
    <h1 class="title" style="font-size: 32px;">Welcome to EdgeFinder</h1>
    <p>Here's a general overview of our services...</p>
    <!-- Add more content about services here -->
  </div>
</main>
<style>
  .main-container {
    padding-top: 60px; /* Offset for fixed header */
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f0f0f0; /* Example background color */
  }

  /* Adjust styles below as needed */
  .content {
    text-align: center;
    padding: 20px;
  }
</style>
