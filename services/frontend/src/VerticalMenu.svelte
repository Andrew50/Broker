<script>
  // VerticalMenu.svelte logic goes here
</script>

<style>
  .menu-container {
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
    background-color: #333;
    width: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .menu ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
  }

  .menu li {
    margin: 0;
    padding: 10px;
  }

  .menu a {
    text-decoration: none;
    color: white;
    font-weight: bold;
  }

  .menu a:hover {
    color: #ff9900;
  }
</style>

<div class="menu-container">
  <div class="menu">
    <ul>
      <li><a href="#">Home</a></li>
      <li><a href="#">About</a></li>
      <li><a href="#">Services</a></li>
      <li><a href="#">Contact</a></li>
    </ul>
  </div>
</div>