function populateIntelligentResultsExpand(results) {
    // populate OpenAI results
    const summaryBox = document.getElementById('summary');
    summaryBox.innerHTML = `<h3>OpenAI Consensus Results</h3><p>The key claim extraction was based on ${results.search_id} comments</p><p>${results.summary}</p>`;
  
    // populate key claims and relevance scores
    const generalConsensusTbody = document.getElementById('general-consensus');
    generalConsensusTbody.innerHTML = '';
    for (let claim of results.key_claims) {
        const tr = document.createElement('tr');
    
        const td1 = document.createElement('td');
        td1.textContent = claim.claim;
    
        const td2 = document.createElement('td');
        td2.textContent = claim.relevance_score;
    
        const td3 = document.createElement('td');
        if (claim.supporting_comments.length > 0) {
            const ul = document.createElement('ul');
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
}
