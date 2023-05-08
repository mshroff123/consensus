document.getElementById("displaytext");

function openIntelligentSearch() {
  window.open('intelligent-search.html');
}

async function searchQuery() {

  const apigClient_intelligent = apigClientFactory.newClient({
    apiKey: 'R5tsFYl3le3dRssgXWlQ96JCQ0ldCJzx58r3tksz'
  });

  const apigClient_reddit = apigClientFactory2.newClient({
    apiKey: 'NCALXpItGB1wjibFxJAhs1fgij8q27ojf0FWQhe0'
  });

  // get query string
  const user_message = document.getElementById('note-textarea').value;
  const searchHistory = JSON.parse(localStorage.getItem("searchHistory")) || [];
  searchHistory.push({
    query: user_message
  });
  localStorage.setItem("searchHistory", JSON.stringify(searchHistory));
  const params = {q: user_message};
  const body = {};
  const additionalParams = {};

  try {
    // send to GET method
    const reddit = await apigClient_reddit.searchGet(params, body, additionalParams);

    const intelligent = await apigClient_intelligent.searchGet(params, body, additionalParams);
    intelligent_result = JSON.stringify(intelligent);
    intelligent_result = JSON.parse(intelligent_result)
    
    populateRawResults(reddit.data);
    
    const intelligentSearch = window.open('intelligent-search.html');
    intelligentSearch.onload = function() {
      intelligentSearch.populateIntelligentResultsExpand(intelligent_result.data);
    }

  } catch (err) {
    console.log("error", err);
  }
}

// use to populate the reddit results
function populateRawResults(searchResults) {
  let html = '<table>';

  // Add table header
  html += '<tr><th>Post Title</th><th>Post Score</th><th>Post URL</th><th>Comment Body</th><th>Comment Score</th><th>Comment URL</th></tr>';

  searchResults.posts.forEach(post => {
    post.comments.forEach(comment => {
      // Add table row for each comment
      html += `<tr><td style="word-wrap: break-word;">${post.post_title}</td><td>${post.post_score}</td><td style="word-wrap: break-word;">${post.post_url}</td><td style="word-wrap: break-word;">${comment.comment_body}</td><td>${comment.comment_score}</td><td style="word-wrap: break-word;">${comment.comment_url}</td></tr>`;
    });
  });

  html += '</table>';

  const resultsDiv = document.getElementById('search-results');
  resultsDiv.innerHTML = html;
}
