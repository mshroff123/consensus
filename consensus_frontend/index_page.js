document.getElementById("displaytext");

function openIntelligentSearch() {
  window.open('intelligent-search.html');
}

async function searchQuery() {

  const resultsDiv = document.getElementById('search-results');
  const intelligentSearchResultsDiv = document.getElementById('intelligent-search-results');
  
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

    console.log("intelligent result sent")
    populateRawResults(reddit.data);

    html = `<div class="loader"></div>`
    const consensusDiv = document.getElementById('consensus-search-results');
    consensusDiv.innerHTML = html;



    const intelligent = await apigClient_intelligent.getClaimsGet(params, body, additionalParams);
    intelligent_result = JSON.stringify(intelligent);
    intelligent_result = JSON.parse(intelligent_result)
    intelligent_result_inputs = intelligent_result.data

    final_claims = []
    for (var i in intelligent_result_inputs["llm_resp_array"]) {
      result = intelligent_result_inputs["llm_resp_array"][i]
      if (result == `\n`) {
        print('bad result')
      }
      else {
        final_claims.push(result.substring(3))
      }
    }

    intelligent_result_inputs["llm_resp_array"] = final_claims

    console.log(intelligent_result_inputs)

    const additionalParamsLambda = {
      headers: {
        "Content-Type": "application/json",
      },
    };

    const intelligent_claims = await apigClient_intelligent.searchPost(params, intelligent_result_inputs, additionalParamsLambda);



    console.log(intelligent_claims)


    const intelligent_claims_result = JSON.stringify(intelligent_claims);
    const intelligent_claims_result_final  = JSON.parse(intelligent_claims_result)
    


    populateIntelligentResultsExpand(intelligent_claims_result_final.data)
    console.log(intelligent_claims_result_final.data)
    
  } catch (err) {
    console.log("error", err);
  }
}

// use to populate the reddit results
function populateRawResults(searchResults) {

  /*
  let html = '<table>';

  // Add table header
  html += '<tr><th>Post Title</th><th>Post Score</th><th>Post URL</th><th>Comment Body</th><th>Comment Score</th><th>Comment URL</th></tr>';

  searchResults.posts.forEach(post => {
    post.comments.forEach(comment => {
      // Add table row for each comment
      html += `<tr style="background-color: white; border-radius: 10px;"><td style="word-wrap: break-word;">${post.post_title}</td><td>${post.post_score}</td><td style="word-wrap: break-word;">${post.post_url}</td><td style="word-wrap: break-word;">${comment.comment_body}</td><td>${comment.comment_score}</td><td style="word-wrap: break-word;">${comment.comment_url}</td></tr>`;
    });
  });

  html += '</table>';


  */
  html = `<div style="font-family: Open Sans; font-size: 22px;">Raw Results:</div>`
  html += `<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; ">`

  searchResults.posts.forEach(post => {
    post.comments.forEach(comment => {
      // Add table row for each commentx
      html += `<div onclick="window.open('${post.post_url}','_blank')"" style=" background-color: white; border-radius: 30px; display:flex; width: 90%; margin-top: 30px; border:none; box-shadow: none; flex-direction:row; align-items: center; justify-content:center;  padding: 20px; border: 1px solid black;"><img src="reddit-logo.png" style="height: 70px; width: 70px; margin-left: 60px"></img><div style="display: flex; flex-direction: column;  align-items: center; justify-content:center;align-self: center; justify-self: center; width: 90%";><div style="font-family: Open Sans; font-size: 18px; font-weight: bold;  color: black; margin: 15px;  width: 80%;">${post.post_title}</div><div style="font-family: Open Sans; font-size: 16px; color: black; margin: 15px; width: 80%;">${comment.comment_body}</div></div></div>`;  });});



  html += "</div>"


  

  const resultsDiv = document.getElementById('reddit-search-results');
  const intelligentSearchResultsDiv = document.getElementById('intelligent-search-results');
  if (resultsDiv.style.display === "none") {
    resultsDiv.style.display = "block";
    intelligentSearchResultsDiv.style.display = "block"
  } else {
    resultsDiv.style.display = "none";
    intelligentSearchResultsDiv.style.display = "none"
  }
  resultsDiv.innerHTML = html;
}

function renderIntelligentResults() {

  const resultsDiv = document.getElementById('reddit-search-results');
  const intelligentSearchResultsDiv = document.getElementById('intelligent-search-results');
  const consensusDiv = document.getElementById('consensus-search-results')


  if (resultsDiv.style.display === "none") {
    // load normal results
    resultsDiv.style.display = "block";
    consensusDiv.style.display = "none"
  } else {
    resultsDiv.style.display = "none";
    consensusDiv.style.display = "flex"
    // load consensus results
  }
}

function displayChildComment(id) {
  td3 = document.getElementById(`td3-${id}`)
  ul = document.getElementById(`child-comment-ul-${id}`)
  ul.style.display = ul.style.display === 'none' ? 'flex' : 'none';
  td3.style.display = td3.style.display === 'none' ? 'flex' : 'none';
  td3.appendChild(ul);
}

function populateIntelligentResultsExpand(results) {
  // populate OpenAI results


  const consensusDiv = document.getElementById('consensus-search-results')
  html = `<div style="font-family: Open Sans; font-size: 22px;display: flex; flex-direction: columns; align-items: center; justify-content:center; ">Consensus Results: Based on ${results.search_id} comments</div>`

  for (var i = 0; i < results.key_claims.length; i++)  {
    claim = results.key_claims[i]
    html += `<div id="${i}" onclick="displayChildComment(this.id)"  style=" background-color: white; border-radius: 30px; display:flex; width: 90%; margin-top: 30px; border:none; box-shadow: none; flex-direction:row; align-items: center; justify-content:center;  padding: 20px; border: 1px solid black;"><div style="width: 70px; font-size: 24px; font-weight: bold; color: #03a9f4; padding: 20px;">${claim.relevance_score}%</div><div style="display: flex; flex-direction: column;  align-items: center; justify-content:center;align-self: center; justify-self: center; width: 90%";><div style="font-family: Open Sans; font-size: 18px; font-weight: bold;  color: black; margin: 15px;  width: 80%; margin-left: -30px;">${claim.claim}</div>`;


    html_id = `td3-${i}`
    html += `<div id=${html_id}  style="display: none; flex-direction: column">`
    // const td3 = document.createElement('div');
    if (claim.supporting_comments.length > 0) {
      /// const ul = document.createElement('div');
      // ul.classList.add('comment-list');
      html += `<div id="child-comment-ul-${i}" style="display: none; flex-direction: column; align-items: center; justify-content:center; padding: 30px">`
      for (let comment of claim.supporting_comments) {
          html += '<div style="width: 80%; background-color: #F2F2F2; margin-top: 20px; flex-direction: row; font-family: Open Sans; padding: 20px;border-radius: 30px;;  border: 1px solid black;"><img src="reddit-logo.png" style="height: 30px; width: 30px; margin-left: 30px; margin-bottom: 20px;"></img>'
          html += `<div style="display: flex; flex-direction: column;  align-items: center; justify-content:center;align-self: center; justify-self: center; width: 100%";>`
          html += `${comment}</div>`
          html += `</div>`
      }

      html += `</div>`


      html += `</div>`

   }

   html += `</div>`

    html += `</div>`
  }

  consensusDiv.innerHTML = html

 
  
  /*
  const summaryBox = document.getElementById('summary');
  summaryBox.innerHTML = `<h3>Consensus Results</h3><p>The key claim extraction was based on ${results.search_id} comments</p><p>${results.summary}</p>`;

  // populate key claims and relevance scores
  const generalConsensusTbody = document.getElementById('general-consensus');
  generalConsensusTbody.innerHTML = '';
  for (let claim of results.key_claims) {
      const tr = document.createElement('tr');
  
      const td1 = document.createElement('td');
      td1.textContent = claim.claim;
  
      const td2 = document.createElement('td');
      td2.textContent = claim.relevance_score;
  
      const td3 = document.createElement('div');
      if (claim.supporting_comments.length > 0) {
          const ul = document.createElement('div');
          ul.classList.add('comment-list');
          for (let comment of claim.supporting_comments) {
              const li = document.createElement('li');
              li.textContent = comment;
              ul.appendChild(li);
          }
          const expandButton = document.createElement('button');
          expandButton.textContent = 'See All Comments';
          expandButton.addEventListener('click', function() {
              ul.style.display = ul.style.display === 'none' ? 'block' : 'none';
              expandButton.textContent = ul.style.display === 'none' ? 'See All Comments' : 'Hide All Comments';
          });
          td3.appendChild(expandButton);
          td3.appendChild(ul);
          ul.style.display = 'none';
      }
  
      tr.appendChild(td1);
      tr.appendChild(td2);
      tr.appendChild(td3);
      generalConsensusTbody.appendChild(tr);
  }
  */

}
