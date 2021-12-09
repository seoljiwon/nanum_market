const onClickCreateComment = async (postId) => {
  try {
    const url = `/post/${postId}/comment/create`;
    const content = document.getElementById("comment__value").value;
    const { data } = await axios.post(url, {
      postId: postId,
      content: content,
    });

    if (data.login_required === true) {
      alert("로그인 후 이용 가능합니다.");
    } else {
      createComment(data.user_id, data.comment_id, data.content);
    }
  } catch (error) {
    console.log(error);
  }
};

const createComment = (user_id, comment_id, content) => {
  const comments = document.getElementById("comments");

  const newComment = document.createElement("div");
  newComment.className = `comment-${comment_id}`;
  newComment.innerHTML = `<span class="comment__writer">${user_id}</span>
                        <span class="comment__date">방금 전</span>
                        <span class="comment__content">${content}</span>`;

  comments.appendChild(newComment);
};
