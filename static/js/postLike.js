const onClickLike = async (postId) => {
  try {
    const options = {
      url: `/post/${postId}/like`,
      method: "POST",
      data: {
        postId: postId,
      },
    };
    const response = await axios(options);
    const responseOK = response && response.status === 200;
    if (responseOK) {
      const data = response.data;
      if (data.login_required === true) {
        alert("로그인 후 이용 가능합니다.");
      } else {
        modifyLike(data.post_id, data.is_liked);
      }
    }
  } catch (error) {
    console.log(error);
  }
};

const modifyLike = (post_id, is_liked) => {
  const like = document.getElementById(`like-${post_id}`).firstElementChild;
  const likeCount = document.getElementById("like__count");

  if (is_liked === true) {
    like.className = "fas fa-thumbs-up";

    const count = Number(likeCount.innerText) + 1;
    likeCount.innerHTML = count;
  } else {
    like.className = "far fa-thumbs-up";

    const count = Number(likeCount.innerText) - 1;
    likeCount.innerHTML = count;
  }
};
