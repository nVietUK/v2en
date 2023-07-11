import { Field, InputType, ObjectType } from '@nestjs/graphql';
import { User } from './user.entity';
import { Entity } from 'typeorm';
import { IsPasswordCorrent, IsUserNameExisted } from './user.validator';

@InputType('UserInput')
export class UserInput {
	constructor(
		username = '',
		familyName = '',
		givenName = '',
		gender = '',
		birthDay: Date = new Date(0, 0, 0),
	) {
		this.username = username;
		this.familyName = familyName;
		this.givenName = givenName;
		this.gender = gender;
		this.birthDay = birthDay;
	}

	@IsUserNameExisted({ message: 'username is existed' })
	@Field(() => String, { nullable: false })
	username: string;

	@Field(() => String, { nullable: false })
	familyName: string;

	@Field(() => String, { nullable: false })
	givenName: string;

	private _birthDay!: string;
	@Field(() => Date)
	get birthDay(): string {
		return this._birthDay
	};
	set birthDay(value: Date) {
		this._birthDay = value.toISOString();
	}

	@Field(() => String, { nullable: false })
	gender?: string;

	@IsPasswordCorrent({
		message:
			'The password must have the minimum length 8 with at leat a special character and more than 3 number',
	})
	@Field(() => String, { nullable: false })
	password?: string;
}

@InputType('LoginInput')
export class LoginInput {
	constructor(
		username = '',
	) {
		this.username = username;
	}

	@Field(() => String, { nullable: false })
	username: string;

	@IsPasswordCorrent({
		message:
			'The password must have the minimum length 8 with at leat a special character and more than 3 number',
	})
	@Field(() => String, { nullable: false })
	password!: string;
}

@Entity()
@ObjectType('UserOutput')
export class UserOutput {
	constructor(
		username = '',
		familyName = '',
		givenName = '',
		gender = '',
		birthDay: Date = new Date(0, 0, 0),
	) {
		this.username = username;
		this.familyName = familyName;
		this.givenName = givenName;
		this.gender = gender;
		this.birthDay = birthDay;
	}

	static fromUser(user: User) {
		return new UserOutput(
			user.username,
			user.familyName,
			user.givenName,
			user.gender,
			new Date(user.birthDay ?? '0/0/0'),
		);
	}

	@Field()
	username: string;

	@Field()
	familyName: string;

	@Field()
	givenName: string;

	@Field()
	gender: string;

	@Field()
	birthDay: Date;
}
