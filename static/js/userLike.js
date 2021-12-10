const onClickLike = async (niceUserId) => {
  try {
    const options = {
      url: `/user/${niceUserId}/like`,
      method: "POST",
      data: {
        niceUserId: niceUserId,
      },
    };
    const response = await axios(options);
    const responseOK = response && response.status === 200;
    if (responseOK) {
      const data = response.data;
      if (data.login_required === true) {
        alert("로그인 후 이용 가능합니다.");
      } else {
        modifyLike(data.nice_user_id, data.is_liked);
      }
    }
  } catch (error) {
    console.log(error);
  }
};

const modifyLike = (nice_user_id, is_liked) => {
  const like = document.getElementById(
    `like-${nice_user_id}`
  ).firstElementChild;
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
