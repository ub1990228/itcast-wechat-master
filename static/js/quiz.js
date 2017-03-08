(function($) {
    $.fn.jquizzy = function(settings) {
        var defaults = {
            questions: null,
            startImg: '../static/image/quiz/start.gif',
            endText: '已结束!',
            shortURL: null,
            sendResultsURL: null,
            resultComments: {
                perfect: '你是爱因斯坦么?',
                excellent: '非常优秀!',
                good: '很好，发挥不错!',
                average: '一般般了。',
                bad: '太可怜了！',
                poor: '好可怕啊！',
                worst: '悲痛欲绝！'
            }
        };
console.log(1);
        var config = $.extend(defaults, settings);
        if (config.questions === null) {
            $(this).html('<div class="intro-container slide-container"><h2 class="qTitle">Failed to parse questions.</h2></div>');
            return;
        }
        var superContainer = $(this),
        questionNumbers = [],
//        introFob = '	<div class="intro-container slide-container"><a class="nav-start" href="#">请认真完成测试题。准备好了吗？<br/><br/><span><img src="'+config.startImg+'"></span></a></div>	',
        exitFob = '<div class="results-container slide-container"><div class="question-number">' + config.endText + '</div><div class="result-keeper"></div></div><div class="notice">请选择一个选项！',//'</div><div class="progress-keeper" ><div class="progress"></div></div>',
        contentFob = '',
        questionsIteratorIndex,
        answersIteratorIndex;
        superContainer.addClass('main-quiz-holder');
        for (questionsIteratorIndex = 0; questionsIteratorIndex < config.questions.length; questionsIteratorIndex++) {
            contentFob += '<div class="slide-container"><div class="question-type">' + '选择题' + '</div><div class="question-number">' + (questionsIteratorIndex + 1) + '/' + config.questions.length + '</div><div class="question">' + config.questions[questionsIteratorIndex].question + '</div><ul class="answers">';
            for (answersIteratorIndex = 0; answersIteratorIndex < config.questions[questionsIteratorIndex].answers.length; answersIteratorIndex++) {
                contentFob += '<li>' + ' <input type="radio"> '+ ' ' + config.questions[questionsIteratorIndex].answers[answersIteratorIndex] + '</li>';
            }
            contentFob += '</ul><div class="nav-container">';
            if (questionsIteratorIndex !== 0) {
                contentFob += '<div class="prev"><a class="nav-previous" href="#">&lt; 上一题</a></div>';
            }
            if (questionsIteratorIndex < config.questions.length - 1) {
                contentFob += '<div class="next"><a class="nav-next" href="#">下一题 &gt;</a></div>';
            } else {
                contentFob += '<div class="next final"><a class="nav-show-result" href="#">完成</a></div>';
            }
            contentFob += '</div></div>';
            questionNumbers.push(config.questions[questionsIteratorIndex].questionNumber);
        }
console.log(2);
        superContainer.html(contentFob + exitFob);
//        var progress = superContainer.find('.progress'),
//        progressKeeper = superContainer.find('.progress-keeper'),
        notice = superContainer.find('.notice'),
//        progressWidth = progressKeeper.width(),
        userAnswers = [],
        questionLength = config.questions.length,
        slidesList = superContainer.find('.slide-container');
        function checkAnswers(answers) {
            var resultArr = [],
            flag = false;
            for (i = 0; i < answers.length; i++) {
                if (answers[i] == userAnswers[i]) {
                    flag = true;
                } else {
                    flag = false;
                }
                resultArr.push(flag);
            }
            return resultArr;
        }
        function roundReloaded(num, dec) {
            var result = Math.round(num * Math.pow(10, dec)) / Math.pow(10, dec);
            return result;
        }
        function judgeSkills(score) {
            var returnString;
            if (score === 100) return config.resultComments.perfect;
            else if (score > 90) return config.resultComments.excellent;
            else if (score > 70) return config.resultComments.good;
            else if (score > 50) return config.resultComments.average;
            else if (score > 35) return config.resultComments.bad;
            else if (score > 20) return config.resultComments.poor;
            else return config.resultComments.worst;
        }
//        progressKeeper.hide();
        notice.hide();
        slidesList.hide().first().fadeIn(200);
        superContainer.find('li').click(function() {
            var thisLi = $(this);
            if (thisLi.hasClass('selected')) {
                thisLi.removeClass('selected');
                thisLi.find("input[type=radio]").prop("checked",false);
            } else {
                thisLi.parents('.answers').children('li').removeClass('selected');
                thisLi.addClass('selected');
                thisLi.parents('.answers').find("input[type=radio]").prop("checked",false);
                $(this).find("input[type=radio]").prop("checked",true);
            }
        });
        superContainer.find('.nav-start').click(function() {
            $(this).parents('.slide-container').fadeOut(200,
            function() {
                $(this).next().fadeIn(200);
//                progressKeeper.fadeIn(500);
            });
            return false;
        });
        superContainer.find('.next').click(function() {
            if ($(this).parents('.slide-container').find('li.selected').length === 0) {
                notice.fadeIn(200);
                return false;
            }
            notice.hide();
            $(this).parents('.slide-container').fadeOut(200,
            function() {
                $(this).next().fadeIn(200);
            });
//            progress.animate({
//                width: progress.width() + Math.round(progressWidth / questionLength)
//            },
//            500);
            return false;
        });
        superContainer.find('.prev').click(function() {
            notice.hide();
            $(this).parents('.slide-container').fadeOut(200,
            function() {
                $(this).prev().fadeIn(200);
            });
//            progress.animate({
//                width: progress.width() - Math.round(progressWidth / questionLength)
 //           },
//            500);
            return false;
        });

        superContainer.find('.final').click(function() {
            if ($(this).parents('.slide-container').find('li.selected').length === 0) {
                notice.fadeIn(300);
                return false;
            }
            superContainer.find('li.selected').each(function(index) {
                userAnswers.push($(this).parents('.answers').children('li').index($(this).parents('.answers').find('li.selected')) + 1);
            });

            var correctAnswers = [];
//console.log(200);
            if (config.sendResultsURL !== null) {
                var myanswers = '[';
                for (r = 0; r < userAnswers.length; r++) {
                    var question = {};
 //                   question["questionNumber"] =  parseInt(r + 1, 10);
 //                   question["userAnswer"] =  userAnswers[r];
                    question = '{"questionNumber":"' + parseInt(r + 1, 10) + '", "userAnswer":"' + userAnswers[r] + '"}';
//console.log(question);
                    if(r < userAnswers.length-1)
                        myanswers +=  question + ',';
                    else
                        myanswers += question;
                    //myanswers.push(JSON.parse(question));
//                      myanswers.push('{"questionNumber":"' + parseInt(r + 1, 10) + '", "userAnswer":"' + userAnswers[r] + '"}');
 //                   myanswers.push(question);
                }
                myanswers += ']'
//console.log(201);
                $.ajaxSettings.async = false;
                $.getJSON('/get_answer/', {'an': myanswers}, function(ret) {
                    if (ret == null) {
                        alert('通讯失败！');
                    } else {

                        correctAnswers=ret;
//console.log("getJSON correctAnswers ");
//console.log(correctAnswers);
/*                        $.each(corects, function(index, array) {
                            console.log(corects[index]);
                            console.log(array);
                            correctAnswers.push(corects[index]);
                            console.log(correctAnswers);
                        });
*/
                    }
                });
            }
//console.log("correctAnswers :");
//console.log(correctAnswers);
//            progressKeeper.hide();
//console.log("userAnswers:");
//console.log(userAnswers);
            var results = checkAnswers(correctAnswers),
            resultSet = '',
            trueCount = 0,
            shareButton = '',
            score,
            url;
//console.log(results);
            if (config.shortURL === null) {
                config.shortURL = window.location
            };
//console.log("config.shortURL");
            for (var i = 0,
            toLoopTill = results.length; i < toLoopTill; i++) {
                if (results[i] === true) {
                    trueCount++;
                    isCorrect = true;
                }
                resultSet += '<div class="result-row">' + (results[i] === true ? "<div class='correct'>"+(i + 1)+"<span></span></div>": "<div class='wrong'>"+(i + 1)+"<span></span></div>");
                resultSet += '<div class="resultsview-qhover">' + config.questions[i].question;
                resultSet += "<ul>";
                for (answersIteratorIndex = 0; answersIteratorIndex < config.questions[i].answers.length; answersIteratorIndex++) {
                    var classestoAdd = '';
                    if (correctAnswers[i] == answersIteratorIndex + 1) {
                        classestoAdd += 'right';
                    }
                    if (userAnswers[i] == answersIteratorIndex + 1) {
                        classestoAdd += ' selected';
                    }
                    resultSet += '<li class="' + classestoAdd + '">' + config.questions[i].answers[answersIteratorIndex] + '</li>';
                }
                resultSet += '</ul></div></div>';
            }
            score = roundReloaded(trueCount / questionLength * 100, 2);
            
            resultSet = '<h2 class="qTitle">' + judgeSkills(score) + '<br/> 您的分数： ' + score + '</h2>' + shareButton + '<div class="jquizzy-clear"></div>' + resultSet + '<div class="jquizzy-clear"></div>';
            superContainer.find('.result-keeper').html(resultSet).show(200);
            superContainer.find('.resultsview-qhover').hide();
            superContainer.find('.result-row').hover(function() {
                $(this).find('.resultsview-qhover').show();
            },
            function() {
                $(this).find('.resultsview-qhover').hide();
            });
            $(this).parents('.slide-container').fadeOut(200,
            function() {
                $(this).next().fadeIn(200);
            });
            return false;
        });
    };
})(jQuery);
